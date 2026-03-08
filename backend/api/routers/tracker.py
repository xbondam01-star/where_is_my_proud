from fastapi import APIRouter
from api.models.schemas import TrackerLog
from api.database import db
from datetime import datetime
from pydantic import Field

router = APIRouter()

@router.post("/tracker/log")
async def log_consumption(log: TrackerLog):
    # Save the consumption to a user_history collection
    history_entry = log.model_dump()
    history_entry["timestamp"] = datetime.utcnow()
    
    result = await db.db.user_history.insert_one(history_entry)
    
    return {"status": "success", "inserted_id": str(result.inserted_id)}
