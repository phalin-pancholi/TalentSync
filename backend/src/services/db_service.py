"""
Database service for TalentSync backend
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from pathlib import Path


class DatabaseService:
    """Service for managing MongoDB connections and operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    async def connect_to_mongo(self):
        """Create database connection"""
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'talentsync')
        
        self.client = AsyncIOMotorClient(mongo_url)
        self.database = self.client[db_name]
        
    async def close_mongo_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        if self.database is None:
            raise RuntimeError("Database not connected")
        return self.database[collection_name]


# Global database service instance
database_service = DatabaseService()