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
        print("  Historical Data loaded.")
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

# Endpoint for Analytics Dashboard (Aggregated Data)
@app.get("/analytics/dashboard")
def get_analytics_data(category: str = None):
    if historical_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    df = historical_data.copy()
    
    # Get all unique categories for the filter dropdown
    all_categories = sorted(df['CATEGORY_NAME'].unique().tolist()) if 'CATEGORY_NAME' in df.columns else []

    # Ensure date column is datetime
    if 'SALES_DATE' in df.columns:
        df['SALES_DATE'] = pd.to_datetime(df['SALES_DATE'])
        df['day_of_week'] = df['SALES_DATE'].dt.day_name()
    
    # Filter by category if provided
    if category and category != "All":
        df = df[df['CATEGORY_NAME'] == category]

    # Helper for Box Plot Stats: [Min, Q1, Median, Q3, Max]
    def get_stats(series):
        if series.empty: return []
        q = series.quantile([0, 0.25, 0.5, 0.75, 1.0])
        return [q[0.0], q[0.25], q[0.5], q[0.75], q[1.0]]

    # 1. Revenue Distribution by Weather (Bar Chart - Mean Revenue)
    weather_dist = df.groupby('WEATHER_CONDITION')['OUR_PRICE'].mean().to_dict()
    
    # 2. Price Consistency by Category (Originally Scatter, now BoxPlot for stability)
    price_consistency = df.groupby('CATEGORY_NAME')['OUR_PRICE'].apply(get_stats).to_dict()
    
    # 3. Sales Distribution by Day of Week (Column Chart - Mean Revenue)
    # day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_dist = df.groupby('day_of_week')['OUR_PRICE'].mean().to_dict()
    
    # 4. Daily Revenue Trend (Line Chart)
    daily_revenue = df.groupby('SALES_DATE')['OUR_PRICE'].sum().reset_index()
    daily_revenue = daily_revenue.sort_values('SALES_DATE')
    trend_data = {
        "dates": daily_revenue['SALES_DATE'].dt.strftime('%Y-%m-%d').tolist(),
        "revenue": daily_revenue['OUR_PRICE'].tolist()
    }
    
    # 5. Total Revenue by Category (Bar Chart)
    cat_rev = df.groupby('CATEGORY_NAME')['OUR_PRICE'].sum().reset_index().sort_values('OUR_PRICE')
    category_revenue = {
        "categories": cat_rev['CATEGORY_NAME'].tolist(),
        "revenue": cat_rev['OUR_PRICE'].tolist()
    }
    
    # 6. Rain Lift Impact (Diverging Bar)
    # Pivot: Index=Category, Columns=Weather, Values=Mean Revenue
    pivot = df.pivot_table(index='CATEGORY_NAME', columns='WEATHER_CONDITION', values='OUR_PRICE', aggfunc='mean').reset_index()
    
    lift_data = {"categories": [], "lift": []}
    if 'Rain' in pivot.columns and 'Clear' in pivot.columns:
        pivot['Rain_Lift'] = ((pivot['Rain'] - pivot['Clear']) / pivot['Clear']) * 100
        pivot = pivot.sort_values('Rain_Lift')
        # Handle NaN/Inf
        pivot['Rain_Lift'] = pivot['Rain_Lift'].fillna(0)
        lift_data = {
            "categories": pivot['CATEGORY_NAME'].tolist(),
            "lift": pivot['Rain_Lift'].tolist()
        }

    return {
        "all_categories": all_categories,
        "weather_distribution": weather_dist,
        "price_consistency": price_consistency,
        "day_distribution": day_dist,
        "daily_trend": trend_data,
        "category_revenue": category_revenue,
        "rain_lift": lift_data
    }

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