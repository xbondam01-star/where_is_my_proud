from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class BeerResponse(BaseModel):
    store: str
    price_per_unit: float
    price_per_liter: float
    volume_liters: float
    valid_until: Optional[date] = None
    is_multipack: bool
    deposit_fee: float
    packaging: str

class HealthCheck(BaseModel):
    status: str
    database: str

class TrackerLog(BaseModel):
    beer_id: str
    count: int
    price: float
