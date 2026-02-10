Here are the **10 most critical code snippets** from your project, curated to show recruiters your skills across the entire Data Engineering lifecycle—from Infrastructure to ML to Application.

I have grouped them by domain so you can easily explain *what* you built and *why* it matters.

### **I. Infrastructure as Code (Terraform & Snowflake)**

*What this shows: You don't click buttons manually; you build reproducible, secure cloud environments.*

**1. Managing Snowflake Resources via Terraform**
*File: `infrastructure/03_snowflake_infrastructure.tf*`

```hcl
# Automating the Data Warehouse creation to ensure environment consistency
resource "snowflake_warehouse" "compute_wh" {
  name           = "COMPUTE_WH"
  warehouse_size = "x-small"
  auto_suspend   = 60
  auto_resume    = true
  comment        = "Main compute resource for ingestion and dbt models."
}

resource "snowflake_schema" "raw_schema" {
  database = snowflake_database.db.name
  name     = "RAW"
  comment  = "Landing zone for immutable source data."
}

```

**2. Secure S3 Integration (The "Handshake")**
*File: `01_snowflake_infrastructure_setup.sql*`

```sql
-- Security Best Practice: Using Storage Integrations instead of hardcoded AWS Keys
CREATE OR REPLACE STORAGE INTEGRATION s3_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::982081062053:role/Snowflake_S3_Connection_Role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://de-project-dynamic-pricing-raw-source/');

```

---

### **II. Advanced Data Engineering (SQL & Logic)**

*What this shows: You can handle complex data transformations and solve unique business problems (like dating aging data).*

**3. The "Time Travel" Shift (Business Logic)**
*File: `02_ingest_core_data.sql*`

```sql
-- Transforming 2017 data to simulate a "Live" 2026 environment
CREATE OR REPLACE VIEW DYNAMIC_PRICING.RAW.orders_current AS
SELECT 
    order_id,
    customer_id,
    order_status,
    -- CRITICAL: Shift dates forward by ~8 years to align historical sales 
    -- with current real-time competitor scraping and weather forecasts.
    DATEADD(day, 2800, order_purchase_timestamp) as order_purchase_timestamp
FROM DYNAMIC_PRICING.RAW.orders;

```

**4. Pattern-Based Ingestion (Data Lake Loading)**
*File: `02_ingest_core_data.sql*`

```sql
-- Efficiently loading partitioned data from S3 using Regex patterns
COPY INTO DYNAMIC_PRICING.RAW.orders
FROM @olist_pricing_stage
PATTERN = '.*orders.*.csv' 
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1, FIELD_OPTIONALLY_ENCLOSED_BY = '"')
ON_ERROR = 'CONTINUE'; -- Fault tolerance for bad records

```

---

### **III. Machine Learning (XGBoost & Feature Engineering)**

*What this shows: You understand not just how to train a model, but how to make it "Business Safe."*

**5. Feature Engineering (The "Why")**
*File: `notebooks/ml_training.ipynb` (Conceptual)*

```python
# Engineering features that capture market dynamics
df['PRICE_RATIO'] = df['AVG_PRICE'] / df['AVG_COMPETITOR_PRICE']
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

# Capturing the "Storm Surge" hypothesis
# (Does Rain + Electronics = Higher Sales?)
df['RAIN_X_ELECTRONICS'] = df.apply(
    lambda x: 1 if x['WEATHER_CONDITION'] == 'Rain' and x['CATEGORY_NAME'] == 'eletronicos' else 0, axis=1
)

```

**6. Monotonic Constraints (The "Safety Rail")**
*File: `notebooks/ml_training.ipynb*`

```python
# CRITICAL: Forcing the model to obey economic laws.
# "As Price goes UP, Demand must go DOWN (or stay flat)."
# We use constraints to prevent the model from recommending infinite price hikes.
model = XGBRegressor(
    objective='reg:squarederror',
    n_estimators=200,
    max_depth=3,
    monotone_constraints='(-1, -1)' # Enforces negative correlation for Price features
)

```

---

### **IV. Backend Engineering (FastAPI)**

*What this shows: You can deploy your model as a scalable, strictly-typed microservice.*

**7. Strict Data Contracts (Pydantic)**
*File: `backend/app/schemas.py*`

```python
# Defining the API Contract to prevent bad data from crashing the model
class PricingScenario(BaseModel):
    category: str = Field(..., example="eletronicos")
    weather: Literal['Clear', 'Rain', 'Cloudy']
    our_price: float = Field(..., gt=0, description="Price must be positive")
    competitor_price: float = Field(..., gt=0)
    
    @validator('category')
    def category_must_exist(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Unknown category: {v}")
        return v

```

**8. Efficient Model Loading (System Design)**
*File: `backend/app/main.py*`

```python
# Loading the model ONCE at startup (Global State) 
# instead of reloading it for every request (Latency Killer)
@app.on_event("startup")
def load_artifacts():
    global model_pipeline, historical_data
    if os.path.exists(MODEL_PATH):
        model_pipeline = joblib.load(MODEL_PATH)
        print("✅ Brain loaded: XGBoost Pipeline ready.")

```

---

### **V. Frontend Engineering (Reflex/Python)**

*What this shows: You are a "Full Stack" Data Engineer who can build tools for stakeholders.*

**9. Async State Management**
*File: `frontend/frontend.py*`

```python
# Managing Application State and Async API calls
class State(rx.State):
    predicted_revenue: float = 0.0
    
    async def get_prediction(self):
        # Asynchronously calling our own Backend API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/predict",
                json={
                    "category": self.category,
                    "our_price": self.our_price,
                    "weather": self.weather
                }
            )
            self.predicted_revenue = response.json()["predicted_revenue"]

```

**10. Interactive Visualization**
*File: `frontend/frontend.py*`

```python
# Rendering the History vs. Competitor Price Chart
rx.recharts.line_chart(
    rx.recharts.line(data_key="OUR_PRICE", stroke="#8884d8"),
    rx.recharts.line(data_key="COMPETITOR_PRICE", stroke="#82ca9d"),
    rx.recharts.x_axis(data_key="SALES_DATE"),
    rx.recharts.tooltip(),
    data=State.chart_data, # Binds directly to the State variable above
    width="100%",
)

```