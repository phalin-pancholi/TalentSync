"""
Main FastAPI application for TalentSync backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from ..services.db_service import database_service
from ..utils.config import config
from ..utils.logging import logger

from .jobs import router as jobs_router
from .matching import router as matching_router
from .candidates import router as candidates_router
from .documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting TalentSync backend...")
    await database_service.connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TalentSync backend...")
    await database_service.close_mongo_connection()
    logger.info("Disconnected from MongoDB")


# Create FastAPI app
app = FastAPI(
    title="TalentSync Backend API",
    description="Modular backend API for TalentSync talent management system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API prefix
api_prefix = "/api"
app.include_router(jobs_router, prefix=api_prefix)
app.include_router(matching_router, prefix=api_prefix)
app.include_router(candidates_router, prefix=api_prefix)
app.include_router(documents_router, prefix=api_prefix)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "TalentSync Backend API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}