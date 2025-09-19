"""
Audit logging service for candidate raw data operations
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from .db_service import database_service


class AuditLogger:
    """Service for audit logging without PII"""
    
    def __init__(self):
        self.collection_name = "audit_logs"
        self.logger = logging.getLogger("audit")
        
        # Configure audit logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def log_operation(self, 
                          operation: str, 
                          user_id: Optional[str] = None,
                          candidate_id: Optional[str] = None,
                          status: str = "success",
                          details: Optional[Dict[str, Any]] = None,
                          error_message: Optional[str] = None):
        """Log an operation to both database and file logs"""
        
        # Sanitize details to remove PII
        sanitized_details = self._sanitize_details(details) if details else {}
        
        audit_entry = {
            "timestamp": datetime.utcnow(),
            "operation": operation,
            "user_id": user_id,
            "candidate_id": candidate_id,
            "status": status,
            "details": sanitized_details,
            "error_message": error_message
        }
        
        # Log to database
        try:
            collection = database_service.get_collection(self.collection_name)
            await collection.insert_one(audit_entry)
        except Exception as e:
            self.logger.error(f"Failed to log to database: {str(e)}")
        
        # Log to file
        log_message = f"Operation: {operation}, Status: {status}"
        if candidate_id:
            log_message += f", Candidate: {candidate_id}"
        if error_message:
            log_message += f", Error: {error_message}"
        
        if status == "success":
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII from details"""
        sanitized = {}
        
        for key, value in details.items():
            if key.lower() in ['email', 'name', 'phone', 'address']:
                # Hash or mask PII fields
                sanitized[key] = f"[REDACTED_{len(str(value))}]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_details(item) if isinstance(item, dict) else f"[ITEM_{i}]" 
                                for i, item in enumerate(value)]
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def log_llm_request(self, 
                            candidate_id: str,
                            model_name: str,
                            input_size: int,
                            output_size: int,
                            status: str,
                            error_message: Optional[str] = None):
        """Log LLM API requests without including content"""
        await self.log_operation(
            operation="llm_request",
            candidate_id=candidate_id,
            status=status,
            details={
                "model": model_name,
                "input_size_chars": input_size,
                "output_size_chars": output_size
            },
            error_message=error_message
        )
    
    async def log_file_upload(self,
                            candidate_id: str,
                            file_count: int,
                            total_size: int,
                            file_types: list,
                            status: str,
                            error_message: Optional[str] = None):
        """Log file upload operations"""
        await self.log_operation(
            operation="file_upload",
            candidate_id=candidate_id,
            status=status,
            details={
                "file_count": file_count,
                "total_size_bytes": total_size,
                "file_types": file_types
            },
            error_message=error_message
        )
    
    async def log_profile_generation(self,
                                   candidate_id: str,
                                   summary_id: str,
                                   status: str,
                                   generation_time_ms: Optional[int] = None,
                                   error_message: Optional[str] = None):
        """Log profile generation operations"""
        await self.log_operation(
            operation="profile_generation",
            candidate_id=candidate_id,
            status=status,
            details={
                "summary_id": summary_id,
                "generation_time_ms": generation_time_ms
            },
            error_message=error_message
        )


# Global audit logger instance
audit_logger = AuditLogger()