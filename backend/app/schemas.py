from pydantic import BaseModel, Field, validator
from typing import Literal

# Input schema for the prediction request
class PricingScenario(BaseModel):
    category: str = Field(..., example="eletronicos", description="Product Category")
    weather: Literal['Clear', 'Rain', 'Cloudy'] = Field(..., example="Clear")
    our_price: float = Field(..., gt=0, example=250.00, description="Proposed Price")
    competitor_price: float = Field(..., gt=0, example=300.00, description="Market Benchmark")
    is_weekend: bool = Field(False, description="Is this for a Saturday/Sunday?")

    # Validate category to ensure it's one I know
    @validator('category')
    def category_must_exist(cls, v):
        allowed = ['eletronicos', 'telefonia', 'audio', 'informatica_acessorios', 'relogios_presentes']
        if v not in allowed:
            raise ValueError(f"Category must be one of {allowed}")
        return v

# Output schema for the response
class PredictionResponse(BaseModel):
    predicted_quantity: float
    predicted_revenue: float
    price_gap: float
    rain_lift_factor: float # How much rain influenced the result