import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.database import connect_to_mongo, close_mongo_connection
from api.routers import beers, tracker
from api.models.schemas import HealthCheck

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from api.scraper.run_scraper import run_scrape_job

# Configure standard logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for finding the best beer deals and tracking consumption."
)

# Initialize Scheduler
scheduler = AsyncIOScheduler()

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "*" # Allowed origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for logging requests and latency
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} | Method: {request.method} | Status: {response.status_code} | Latency: {process_time:.4f}s")
    return response

# Database connection events & Scheduler
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    
    # Start the scraper job (run immediately, then every 12 hours)
    scheduler.add_job(run_scrape_job, "interval", hours=12)
    scheduler.start()
    logger.info("Background Scraper Scheduler started (Interval: 12 hours).")
    # Uncomment to run immediately on startup:
    # run_scrape_job()

@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    await close_mongo_connection()

# Routers
app.include_router(beers.router, tags=["beers"])
app.include_router(tracker.router, tags=["tracker"])

@app.get("/", response_model=HealthCheck, tags=["health"])
async def health_check():
    return {"status": "ok", "database": "connected"}
