"""
Service for Gemini LLM integration and profile summary generation
"""
import os
import logging
from typing import Dict, Any, Optional
import json
import httpx
from datetime import datetime

from ..models.candidate_raw_data import ProfileSummary
from .audit_service import audit_logger


class GeminiLLMService:
    """Service for integrating with Gemini LLM API"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        self.model_name = "Gemini-1.5-flash"
        
        if not self.api_key:
            logging.warning("GEMINI_API_KEY not found in environment variables")
    
    def _create_profile_prompt(self, candidate_data: Dict[str, Any]) -> str:
        """Create a structured prompt for profile generation"""
        
        files_text = ""
        for file_info in candidate_data.get("files", []):
            files_text += f"\n--- {file_info['filename']} ---\n"
            files_text += file_info['content']
            files_text += "\n"
        
        prompt = f"""
Generate a professional profile summary for this candidate based on their resume and feedback data.

Candidate Email: {candidate_data.get('email', 'N/A')}

Content:
{files_text}

Please create a professional profile summary in the following format:

Professional Summary
[2-3 sentences summarizing their experience and key skills]

Education
[List education background]

Key Strengths
[Bullet points of key strengths and skills]

Technical Skills
Programming Languages: [list]
Frontend: [list]
Databases: [list]
DevOps: [list]

Professional Experience
[Summary of work experience and achievements]

Project Summary
[Brief overview of notable projects or contributions]

Keep the response professional, concise, and well-structured. Focus on the candidate's strengths and relevant experience.
"""
        return prompt
    
    async def generate_profile_summary(self, candidate_data: Dict[str, Any]) -> str:
        """Generate profile summary using Gemini LLM"""
        
        if not self.api_key:
            raise Exception("Gemini API key not configured")
        
        prompt = self._create_profile_prompt(candidate_data)
        
        # Prepare request payload
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 2048,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}?key={self.api_key}",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logging.error(f"Gemini API error: {response.status_code} - {response.text}")
                    raise Exception(f"Gemini API returned status {response.status_code}")
                
                result = response.json()
                
                # Extract generated text from response
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0]["text"]
                
                raise Exception("No valid response from Gemini API")
                
        except httpx.TimeoutException:
            logging.error("Gemini API request timed out")
            raise Exception("Gemini API request timed out")
        except Exception as e:
            logging.error(f"Error calling Gemini API: {str(e)}")
            raise Exception(f"Failed to generate profile summary: {str(e)}")


class ProfileSummaryService:
    """Service for managing profile summaries"""
    
    def __init__(self):
        self.collection_name = "profile_summaries"
        self.gemini_service = GeminiLLMService()
    
    async def create_profile_summary(self, candidate_id: str, candidate_data: Dict[str, Any]) -> ProfileSummary:
        """Create a new profile summary using Gemini LLM"""
        
        start_time = datetime.utcnow()
        
        # Create initial profile summary record
        profile_summary = ProfileSummary(
            candidate_id=candidate_id,
            summary_text="",
            llm_model=self.gemini_service.model_name,
            status="pending"
        )
        
        # Store initial record
        from .db_service import database_service
        collection = database_service.get_collection(self.collection_name)
        await collection.insert_one(profile_summary.dict())
        
        try:
            # Generate summary using Gemini LLM
            summary_text = await self.gemini_service.generate_profile_summary(candidate_data)
            
            # Calculate generation time
            generation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update record with success
            await collection.update_one(
                {"summary_id": profile_summary.summary_id},
                {
                    "$set": {
                        "summary_text": summary_text,
                        "status": "success",
                        "generated_at": datetime.utcnow()
                    }
                }
            )
            
            profile_summary.summary_text = summary_text
            profile_summary.status = "success"
            
            # Log successful LLM request
            await audit_logger.log_llm_request(
                candidate_id=candidate_id,
                model_name=self.gemini_service.model_name,
                input_size=len(str(candidate_data)),
                output_size=len(summary_text),
                status="success"
            )
            
            await audit_logger.log_profile_generation(
                candidate_id=candidate_id,
                summary_id=profile_summary.summary_id,
                status="success",
                generation_time_ms=int(generation_time)
            )
            
        except Exception as e:
            # Update record with error
            error_message = str(e)
            await collection.update_one(
                {"summary_id": profile_summary.summary_id},
                {
                    "$set": {
                        "status": "error",
                        "error_message": error_message,
                        "generated_at": datetime.utcnow()
                    }
                }
            )
            
            profile_summary.status = "error"
            profile_summary.error_message = error_message
            
            # Log failed LLM request
            await audit_logger.log_llm_request(
                candidate_id=candidate_id,
                model_name=self.gemini_service.model_name,
                input_size=len(str(candidate_data)),
                output_size=0,
                status="error",
                error_message=error_message
            )
            
            await audit_logger.log_profile_generation(
                candidate_id=candidate_id,
                summary_id=profile_summary.summary_id,
                status="error",
                error_message=error_message
            )
            
            logging.error(f"Profile generation failed for candidate {candidate_id}: {error_message}")
        
        return profile_summary
    
    async def get_profile_summary(self, summary_id: str) -> Optional[ProfileSummary]:
        """Get profile summary by ID"""
        from .db_service import database_service
        collection = database_service.get_collection(self.collection_name)
        
        summary_data = await collection.find_one({"summary_id": summary_id})
        if summary_data:
            return ProfileSummary(**summary_data)
        return None


# Global service instances
gemini_llm_service = GeminiLLMService()
profile_summary_service = ProfileSummaryService()