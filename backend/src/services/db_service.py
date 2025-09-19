"""
Database service for TalentSync backend
"""
from motor.motor_asyncio import AsyncIOMotorClient
from motor import motor_asyncio
from pymongo import IndexModel, ASCENDING
from typing import Optional
import os
import gridfs
from pathlib import Path


class DatabaseService:
    """Service for managing MongoDB connections and operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.gridfs_bucket = None
        
    async def connect_to_mongo(self):
        """Create database connection"""
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'talentsync')
        
        self.client = AsyncIOMotorClient(mongo_url)
        self.database = self.client[db_name]
        
        # Initialize GridFS for file storage
        self.gridfs_bucket = motor_asyncio.AsyncIOMotorGridFSBucket(self.database)
        
        # Create indexes for candidate raw data
        await self.create_indexes()
        
    async def create_indexes(self):
        """Create MongoDB indexes for candidate raw data and profile summaries"""
        # Indexes for candidate_raw_data collection
        candidate_collection = self.database.candidate_raw_data
        await candidate_collection.create_index([("email", ASCENDING)])
        await candidate_collection.create_index([("candidate_id", ASCENDING)], unique=True)
        
        # Indexes for profile_summaries collection
        profile_collection = self.database.profile_summaries
        await profile_collection.create_index([("candidate_id", ASCENDING)])
        await profile_collection.create_index([("summary_id", ASCENDING)], unique=True)
        
    async def close_mongo_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        if self.database is None:
            raise RuntimeError("Database not connected")
        return self.database[collection_name]
    
    async def store_file_gridfs(self, file_data: bytes, filename: str, content_type: str) -> str:
        """Store file in GridFS and return file ID"""
        if self.gridfs_bucket is None:
            raise RuntimeError("GridFS not initialized")
        
        file_id = await self.gridfs_bucket.upload_from_stream(
            filename,
            file_data,
            metadata={"content_type": content_type}
        )
        return str(file_id)
    
    async def get_file_gridfs(self, file_id: str) -> bytes:
        """Retrieve file from GridFS by ID"""
        if self.gridfs_bucket is None:
            raise RuntimeError("GridFS not initialized")
        
        grid_out = await self.gridfs_bucket.open_download_stream(file_id)
        return await grid_out.read()


# Global database service instance
database_service = DatabaseService()