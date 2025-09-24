from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import logging
from service import ZohoSyncService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zoho Sync Service",
    description="Service to sync employee data from Zoho People Plus and generate candidate details",
    version="1.0.0"
)

# Global service instance
sync_service = None


class SyncRequest(BaseModel):
    access_token: Optional[str] = None
    sync_interval: Optional[int] = None


class SyncResponse(BaseModel):
    message: str
    sync_result: Optional[Dict[str, Any]] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the sync service on startup"""
    global sync_service
    try:
        sync_service = ZohoSyncService()
        await sync_service.initialize()
        logger.info("Zoho Sync Service initialized successfully")
        
        # Start periodic sync in background
        asyncio.create_task(sync_service.start_periodic_sync())
        logger.info("Periodic sync started")
        
    except Exception as e:
        logger.error(f"Failed to initialize sync service: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global sync_service
    if sync_service:
        await sync_service.close()
        logger.info("Sync service closed")


@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"message": "Zoho Sync Service is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "zoho-sync-service"}


@app.post("/sync", response_model=SyncResponse)
async def trigger_manual_sync(sync_request: SyncRequest = None):
    """Trigger a manual sync operation"""
    global sync_service
    
    if not sync_service:
        raise HTTPException(status_code=500, detail="Sync service not initialized")
    
    try:
        logger.info("Manual sync triggered")
        sync_result = await sync_service.run_sync()
        
        return SyncResponse(
            message="Manual sync completed",
            sync_result=sync_result
        )
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/candidates")
async def get_candidates() -> List[Dict[str, Any]]:
    """Retrieve all generated candidate details"""
    global sync_service
    
    if not sync_service:
        raise HTTPException(status_code=500, detail="Sync service not initialized")
    
    try:
        candidates = await sync_service.get_all_candidates()
        logger.info(f"Retrieved {len(candidates)} candidates")
        return candidates
        
    except Exception as e:
        logger.error(f"Failed to retrieve candidates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidates: {str(e)}")


@app.get("/candidates/{employee_id}")
async def get_candidate_by_employee_id(employee_id: str) -> Dict[str, Any]:
    """Retrieve candidate details for a specific employee"""
    global sync_service
    
    if not sync_service:
        raise HTTPException(status_code=500, detail="Sync service not initialized")
    
    try:
        candidate = await sync_service.candidates_collection.find_one(
            {"employee_id": employee_id}
        )
        
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate not found for employee: {employee_id}")
        
        # Convert ObjectId to string for JSON serialization
        candidate["_id"] = str(candidate["_id"])
        
        logger.info(f"Retrieved candidate for employee: {employee_id}")
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve candidate for employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidate: {str(e)}")


@app.get("/sync/status")
async def get_sync_status() -> Dict[str, Any]:
    """Get the current sync status"""
    global sync_service
    
    if not sync_service:
        raise HTTPException(status_code=500, detail="Sync service not initialized")
    
    try:
        status = await sync_service.sync_status_collection.find_one({})
        
        if not status:
            return {"message": "No sync operations completed yet"}
        
        # Convert ObjectId to string for JSON serialization
        status["_id"] = str(status["_id"])
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to retrieve sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sync status: {str(e)}")


@app.get("/employees")
async def get_employees() -> List[Dict[str, Any]]:
    """Retrieve all employee records"""
    global sync_service
    
    if not sync_service:
        raise HTTPException(status_code=500, detail="Sync service not initialized")
    
    try:
        cursor = sync_service.employees_collection.find({})
        employees = []
        async for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            doc["_id"] = str(doc["_id"])
            employees.append(doc)
        
        logger.info(f"Retrieved {len(employees)} employee records")
        return employees
        
    except Exception as e:
        logger.error(f"Failed to retrieve employees: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employees: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)