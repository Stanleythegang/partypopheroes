from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Import module routers
from modules import auth, products, ai, kyc

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Inject database into modules
auth.set_db(db)
kyc.set_db(db)
products.set_db(db)

# Create the main app
app = FastAPI(
    title="Hamro API",
    description="Backend API for Hamro Platform - E-commerce with Authentication & KYC",
    version="2.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "Hello from Hamro",
        "platform": "Hamro",
        "version": "2.0.0",
        "status": "running",
        "features": ["authentication", "kyc", "products", "ai"]
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "service": "hamro-backend",
        "modules": ["auth", "kyc", "products", "ai"]
    }

# Include module routers
api_router.include_router(auth.router)
api_router.include_router(kyc.router)
api_router.include_router(products.router)
api_router.include_router(ai.router)

# Include the main router in the app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Hamro Backend API starting up...")
    logger.info(f"📦 Database: {os.environ['DB_NAME']}")
    logger.info("✅ All modules loaded successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("👋 Shutting down Hamro Backend API...")
    client.close()
