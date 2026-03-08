from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from api.models.schemas import BeerResponse
from api.database import db

router = APIRouter()

@router.get("/deals", response_model=List[BeerResponse])
async def get_deals(
    store: Optional[str] = Query(None, description="Filter deals by store name (case-insensitive)"),
    only_multipack: Optional[bool] = Query(None, description="Filter for multipacks only")
):
    query = {}
    
    if store:
        # Case insensitive regex match for store
        query["store"] = {"$regex": store, "$options": "i"}
        
    if only_multipack is not None:
        query["is_multipack"] = only_multipack
        
    # Query MongoDB for active deals, sorted by price_per_liter ascending
    cursor = db.db.deals.find(query).sort("price_per_liter", 1)
    deals = await cursor.to_list(length=100)
    
    return deals

@router.get("/deals/best", response_model=BeerResponse)
async def get_best_deal():
    # Returns only the single cheapest record currently in the database
    best_deal = await db.db.deals.find_one(sort=[("price_per_liter", 1)])
    if not best_deal:
        raise HTTPException(status_code=404, detail="No deals found")
    return best_deal
