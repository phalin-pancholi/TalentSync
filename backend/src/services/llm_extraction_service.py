"""
LLM extraction service for TalentSync backend
Uses Langchain and Gemini to extract structured job information from text
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from pydantic import ValidationError

from ..models.job_posting import JobPostingLLMCreate

logger = logging.getLogger(__name__)


class LLMExtractionService:
    """Service for extracting structured job information using LLM"""
    
    def __init__(self):
        """Initialize the LLM extraction service"""
        # Get API key from environment
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
        
        # Initialize Gemini model via Langchain
        self.llm = None
        if self.api_key:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=self.api_key,
                    temperature=0.1  # Low temperature for consistent extraction
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
    
    def extract_job_info(self, text_content: str) -> JobPostingLLMCreate:
        """
        Extract structured job information from text content
        
        Args:
            text_content: Raw text content from job description
            
        Returns:
            JobPostingLLMCreate: Extracted job information with optional fields
            
        Raises:
            Exception: If LLM service is unavailable or extraction fails
        """
        if not self.llm:
            raise Exception("LLM service is not available. Please check API key configuration.")
        
        if not text_content.strip():
            raise ValueError("Empty text content provided for extraction")
        
        try:
            # Create extraction prompt
            prompt = self._create_extraction_prompt(text_content)
            
            # Call LLM
            messages = [
                SystemMessage(content="You are an expert at extracting structured job information from job descriptions. Always respond with valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse response
            job_data = self._parse_llm_response(response.content)
            
            # Create and validate model
            job_posting = JobPostingLLMCreate(**job_data)
            
            logger.info(f"Successfully extracted job information. Fields found: {list(job_data.keys())}")
            return job_posting
            
        except Exception as e:
            logger.error(f"Failed to extract job information: {str(e)}")
            raise Exception(f"LLM extraction failed: {str(e)}")
    
    def _create_extraction_prompt(self, text_content: str) -> str:
        """Create a prompt for job information extraction"""
        return f"""
Extract job information from the following text and return it as a JSON object with these fields:
- title: Job title (string or null)
- description: Job description (string or null)
- skills: Required skills as an array of strings (array or null)
- experience_level: Experience level required (string or null)
- department: Department/team (string or null)
- location: Job location (string or null)

Rules:
1. Only extract information that is explicitly mentioned in the text
2. If a field is not mentioned or unclear, set it to null
3. For skills, extract individual skills as separate array items
4. For experience_level, use terms like "entry-level", "mid-level", "senior-level", "3+ years", etc.
5. Return ONLY valid JSON, no additional text

Job Description Text:
{text_content}

JSON Response:
"""
    
    def _parse_llm_response(self, response_content: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            # Try to find JSON in the response
            response_content = response_content.strip()
            
            # If response starts with ```json, extract the JSON part
            if response_content.startswith('```json'):
                start = response_content.find('{')
                end = response_content.rfind('}') + 1
                response_content = response_content[start:end]
            elif response_content.startswith('```'):
                start = response_content.find('{')
                end = response_content.rfind('}') + 1
                response_content = response_content[start:end]
            
            # Parse JSON
            job_data = json.loads(response_content)
            
            # Ensure all expected fields exist with None as default
            expected_fields = ['title', 'description', 'skills', 'experience_level', 'department', 'location']
            for field in expected_fields:
                if field not in job_data:
                    job_data[field] = None
            
            # Clean up empty strings and convert to None
            for key, value in job_data.items():
                if isinstance(value, str) and not value.strip():
                    job_data[key] = None
                elif isinstance(value, list) and not value:
                    job_data[key] = None
            
            return job_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {response_content}")
            # Return empty structure if parsing fails
            return {
                'title': None,
                'description': text_content[:200] if text_content else None,  # Fallback to truncated text
                'skills': None,
                'experience_level': None,
                'department': None,
                'location': None
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing LLM response: {str(e)}")
            raise Exception(f"Failed to parse LLM response: {str(e)}")
    
    def is_service_available(self) -> bool:
        """Check if the LLM service is available"""
        return self.llm is not None and self.api_key is not None