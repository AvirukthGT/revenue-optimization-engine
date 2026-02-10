from fastapi import FastAPI, HTTPException
from .schemas import PricingScenario, PredictionResponse
import joblib
import pandas as pd
import os

# Initialize the FastAPI app
app = FastAPI(
    title="Revenue Optimization Engine API",
    description="XGBoost-powered pricing engine for retail forecasting.",
    version="1.0.0"
)

# Load the model globally to save time on requests
MODEL_PATH = "backend/models/revenue_model.pkl"
model_pipeline = None

@app.on_event("startup")
def load_model():
    global model_pipeline
    if os.path.exists(MODEL_PATH):
        model_pipeline = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    else:
        print(f"Critical Error: Model not found at {MODEL_PATH}")

# Variable to hold historical data for the frontend
HISTORY_PATH = "backend/data/history.parquet"
historical_data = None

@app.on_event("startup")
def load_data():
    global historical_data
    # Load the Parquet file into memory (It's much faster this way)
    if os.path.exists(HISTORY_PATH):
        historical_data = pd.read_parquet(HISTORY_PATH)
        print("Historical Data loaded.")
    else:
        print("Warning: No history.parquet found.")

# Endpoint to serve historical data for the charts
@app.get("/history/{category}")
def get_category_history(category: str):
    if historical_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Filter for the requested category
    filtered = historical_data[historical_data['CATEGORY_NAME'] == category]
    
    if filtered.empty:
        raise HTTPException(status_code=404, detail="Category not found")

    # Resample/Aggregate if needed (Optional: Limit to last 30 entries for speed)
    # I return a list of dictionaries so the frontend can easily graph it
    result = filtered.to_dict(orient="records")
    return result

# Endpoint to predict sales
@app.post("/predict", response_model=PredictionResponse)
def predict_demand(scenario: PricingScenario):
    if not model_pipeline:
        raise HTTPException(status_code=500, detail="Model not initialized.")
    
    # Prepare the features for the model
    # Manually constructing the DataFrame to match training data
    input_df = pd.DataFrame([{
        'CATEGORY_NAME': scenario.category,
        'WEATHER_CONDITION': scenario.weather,
        'AVG_PRICE': scenario.our_price,
        'PRICE_RATIO': scenario.our_price / scenario.competitor_price, # Calculated here
        'is_weekend': 1 if scenario.is_weekend else 0
    }])

    # Run the prediction
    try:
        predicted_qty = model_pipeline.predict(input_df)[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Calculate revenue and other metrics
    revenue = predicted_qty * scenario.our_price
    gap = scenario.competitor_price - scenario.our_price
    
    # Simple heuristic for Rain Lift based on my analysis
    lift = 0.0
    if scenario.weather == 'Rain' and scenario.category == 'eletronicos':
        lift = 0.20 

    return {
        "predicted_quantity": max(0, float(predicted_qty)), # No negative sales
        "predicted_revenue": max(0, float(revenue)),
        "price_gap": float(gap),
        "rain_lift_factor": lift
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "active", "model_loaded": model_pipeline is not None}