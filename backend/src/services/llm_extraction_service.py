"""
LLM extraction service for TalentSync backend
Uses Langchain and Gemini to extract structured job information from text
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
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
    
    async def extract_candidate_info(self, text_content: str):
        """
        Extract structured candidate information from text content (resume/CV)
        
        Args:
            text_content: Raw text content from candidate document
            
        Returns:
            CandidateLLMCreate: Extracted candidate information with optional fields
            
        Raises:
            Exception: If LLM service is unavailable or extraction fails
        """
        if not self.llm:
            raise Exception("LLM service is not available. Please check API key configuration.")
        
        if not text_content.strip():
            raise ValueError("Empty text content provided for extraction")
        
        try:
            # Create extraction prompt for candidate
            prompt = self._create_candidate_extraction_prompt(text_content)
            
            # Call LLM
            messages = [
                SystemMessage(content="You are an expert at extracting structured candidate information from resumes and CVs. Always respond with valid JSON."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse response
            candidate_data = self._parse_candidate_llm_response(response.content, text_content)
            
            # Import here to avoid circular imports
            from ..models.candidate import CandidateLLMCreate
            
            # Create and validate model
            candidate = CandidateLLMCreate(**candidate_data)
            
            logger.info(f"Successfully extracted candidate information. Fields found: {list(candidate_data.keys())}")
            return candidate
            
        except Exception as e:
            logger.error(f"Failed to extract candidate information: {str(e)}")
            raise Exception(f"LLM extraction failed: {str(e)}")
    
    def _create_candidate_extraction_prompt(self, text_content: str) -> str:
        """Create a prompt for candidate information extraction"""
        return f"""
Extract candidate information from the following resume/CV text and return it as a JSON object with these fields:
- name: Full name of the candidate (string or null)
- email: Email address (string or null)
- phone: Phone number (string or null)
- skills: Skills and technologies as an array of strings (array or null)
- experience: Work experience summary or years of experience (string or null)
- location: Current location, preferred location, or address (string or null)
- education: Educational background (string or null)
- summary: Professional summary or objective (string or null)

Rules:
1. Only extract information that is explicitly mentioned in the text
2. If a field is not mentioned or unclear, set it to null
3. For skills, extract individual skills and technologies as separate array items
4. For experience, provide a brief summary of work history or years (e.g., "5 years", "Senior Developer with 3+ years")
5. For location, extract city, state/country, or any location mentioned (e.g., "San Francisco, CA", "Remote", "Willing to relocate")
6. For education, include degrees, institutions, and relevant details
7. Return ONLY valid JSON, no additional text

Resume/CV Text:
{text_content}

JSON Response:
"""
    
    def _parse_candidate_llm_response(self, response_content: str, text_content: str) -> Dict[str, Any]:
        """Parse and validate LLM response for candidate extraction"""
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
            candidate_data = json.loads(response_content)
            
            # Ensure all expected fields exist with None as default
            expected_fields = ['name', 'email', 'phone', 'skills', 'experience', 'location', 'education', 'summary']
            for field in expected_fields:
                if field not in candidate_data:
                    candidate_data[field] = None
            
            # Clean up empty strings and convert to None
            for key, value in candidate_data.items():
                if isinstance(value, str) and not value.strip():
                    candidate_data[key] = None
                elif isinstance(value, list) and not value:
                    candidate_data[key] = None
            
            return candidate_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {response_content}")
            # Return empty structure if parsing fails - allow partial data
            return {
                'name': None,
                'email': None,
                'phone': None,
                'skills': None,
                'experience': None,
                'location': None,  # Added location field
                'education': None,
                'summary': text_content[:200] if text_content else None  # Fallback to truncated text
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing candidate LLM response: {str(e)}")
            raise Exception(f"Failed to parse candidate LLM response: {str(e)}")

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
                'description': None,
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

    async def generate_profile_summary(self, candidate_data: Dict[str, Any], feedback_data: List[str] = None) -> str:
        """
        Generate a professional profile summary for a candidate using Gemini LLM
        
        Args:
            candidate_data: Dictionary containing candidate information (name, skills, experience, etc.)
            feedback_data: List of feedback strings about the candidate
            
        Returns:
            str: Generated profile summary text
            
        Raises:
            Exception: If LLM service is unavailable or generation fails
        """
        if not self.llm:
            raise Exception("LLM service is not available. Please check API key configuration.")
        
        try:
            # Create profile summary prompt
            prompt = self._create_profile_summary_prompt(candidate_data, feedback_data)
            
            # Call LLM
            messages = [
                SystemMessage(content="You are an expert HR professional who creates compelling, professional profile summaries for candidates. Focus on highlighting strengths, achievements, and potential value to employers."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Clean and return the response
            profile_summary = response.content.strip()
            
            logger.info(f"Successfully generated profile summary for candidate: {candidate_data.get('name', 'Unknown')}")
            return profile_summary
            
        except Exception as e:
            logger.error(f"Failed to generate profile summary: {str(e)}")
            raise Exception(f"Profile summary generation failed: {str(e)}")

    def _create_profile_summary_prompt(self, candidate_data: Dict[str, Any], feedback_data: List[str] = None) -> str:
        """Create a prompt for profile summary generation"""
        
        # Extract candidate information
        name = candidate_data.get('name', 'Candidate')
        email = candidate_data.get('email', '')
        phone = candidate_data.get('phone', '')
        skills = candidate_data.get('skills', [])
        experience = candidate_data.get('experience', '')
        education = candidate_data.get('education', '')
        summary = candidate_data.get('summary', '')
        raw_text = candidate_data.get('raw_text', '')
        
        # Format skills
        skills_text = ', '.join(skills) if skills else 'Not specified'
        
        # Format feedback
        feedback_text = ""
        if feedback_data:
            feedback_text = "\n\nFeedback and Additional Information:\n" + "\n".join([f"- {fb}" for fb in feedback_data])
        
        return f"""
Generate a professional profile summary for the following candidate. The summary should be comprehensive, highlighting key strengths, technical skills, experience, and professional value. Use the provided template structure but adapt the content based on the candidate's actual information.

CANDIDATE INFORMATION:
Name: {name}
Email: {email}
Phone: {phone}
Skills: {skills_text}
Experience: {experience}
Education: {education}
Professional Summary: {summary}
Raw Resume/CV Text: {raw_text}{feedback_text}

REQUIRED TEMPLATE STRUCTURE:
Professional Summary
[3-4 sentences highlighting role, experience, key technologies, and professional strengths]

Education
[Educational background including degrees, institutions, certifications]

Key Strengths
[3-5 bullet points of key professional strengths and abilities]

Technical Skills
Programming Languages: [list relevant languages]
Frontend: [frontend technologies]
Backend: [backend technologies]  
Databases: [database technologies]
DevOps: [DevOps tools and practices]
Other: [other relevant technical skills]

Professional Experience
[Summary of work experience, key contributions, and achievements]

Project Summary:
[Brief overview of notable projects or achievements]

INSTRUCTIONS:
1. Use ONLY the information provided - do not make up details
2. If information is missing for a section, write "Not specified" or leave appropriate blanks
3. Focus on professional language and highlight value proposition
4. Adapt the technical skills section based on the candidate's actual skills
5. Make the summary compelling while staying factual
6. If experience level is not clear, infer from the available information
7. Return the formatted summary ready for PDF generation

Generate the profile summary now:
"""