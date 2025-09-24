import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from models import EmployeeRecord, CandidateDetails, SyncStatus
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZohoSyncService:
    def __init__(self):
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://admin:password123@mongodb:27017/talentsync_db?authSource=admin")
        self.db_name = os.getenv("DB_NAME", "talentsync_db")
        self.zoho_access_token = os.getenv("ZOHO_ACCESS_TOKEN")
        self.sync_interval = int(os.getenv("SYNC_INTERVAL", "5"))
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.zoho_access_token:
            logger.error("ZOHO_ACCESS_TOKEN environment variable is required")
            raise ValueError("ZOHO_ACCESS_TOKEN is required")
        
        if not self.google_api_key:
            logger.error("GOOGLE_API_KEY environment variable is required")
            raise ValueError("GOOGLE_API_KEY is required")
        
        # Initialize Google Generative AI
        genai.configure(api_key=self.google_api_key)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # Updated model name
            google_api_key=self.google_api_key,
            temperature=0.1
        )
        
        self.client = None
        self.db = None
        self.employees_collection = None
        self.candidates_collection = None
        self.sync_status_collection = None

    async def initialize(self):
        """Initialize database connection"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            self.employees_collection = self.db.employees
            self.candidates_collection = self.db.candidates
            self.sync_status_collection = self.db.sync_status
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def fetch_employees_from_zoho(self) -> List[Dict[str, Any]]:
        """Fetch employees from Zoho People Plus API"""
        try:
            url = "https://people.zoho.in/people/api/forms/P_EmployeeView/records"
            headers = {
                "Authorization": f"Zoho-oauthtoken {self.zoho_access_token}",
                "Content-Type": "application/json"
            }
            
            # Add limit to respect the 50 employees per sync constraint
            params = {"limit": 50}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different possible response formats from Zoho API
            employees = []
            if isinstance(data, list):
                # If data is directly a list of employees
                employees = data[:50]  # Ensure we don't exceed our limit
            elif isinstance(data, dict):
                # If data is wrapped in response object
                if "response" in data:
                    response_data = data["response"]
                    if isinstance(response_data, dict) and "result" in response_data:
                        employees = response_data["result"]
                    elif isinstance(response_data, list):
                        employees = response_data
                elif "result" in data:
                    employees = data["result"]
                elif "data" in data:
                    employees = data["data"]
                else:
                    # If data is a dict but no known wrapper, try to use it directly
                    logger.warning(f"Unknown Zoho API response format: {list(data.keys())}")
                    employees = [data] if data else []
            
            # Ensure employees is a list and limit to 50
            if not isinstance(employees, list):
                employees = []
            else:
                employees = employees[:50]
            
            logger.info(f"Fetched {len(employees)} employees from Zoho")
            return employees
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch employees from Zoho: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching employees: {e}")
            raise

    async def store_employee(self, employee_data: Dict[str, Any]) -> EmployeeRecord:
        """Store employee record in database"""
        try:
            # Extract key fields with defaults - handle Zoho API field names
            employee_id = employee_data.get("Employee ID", employee_data.get("Employeeid", ""))
            
            # Handle name fields - try different field name variations
            first_name = employee_data.get("First Name", employee_data.get("Firstname", ""))
            last_name = employee_data.get("Last Name", employee_data.get("Lastname", ""))
            name = f"{first_name} {last_name}".strip()
            
            job_title = employee_data.get("Designation", "")
            department = employee_data.get("Department", "")
            
            # Extract contact info with proper field names
            contact_info = {
                "email": employee_data.get("Email address", employee_data.get("Emailid", "")),
                "phone": employee_data.get("Personal Mobile Number", employee_data.get("Mobile", "")),
                "address": employee_data.get("Present Address", employee_data.get("Address", ""))
            }
            
            employee_record = EmployeeRecord(
                employee_id=employee_id,
                name=name,
                contact_info=contact_info,
                job_title=job_title,
                department=department,
                all_other_fields=employee_data,
                updated_at=datetime.utcnow()
            )
            
            # Upsert employee record
            result = await self.employees_collection.replace_one(
                {"employee_id": employee_id},
                employee_record.model_dump(by_alias=True, exclude={"id"}),
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"Created new employee record: {employee_id}")
            else:
                logger.info(f"Updated employee record: {employee_id}")
            
            return employee_record
            
        except Exception as e:
            logger.error(f"Failed to store employee {employee_data.get('Employee ID', employee_data.get('Employeeid', 'unknown'))}: {e}")
            raise

    async def generate_candidate_details_with_llm(self, employee_record: EmployeeRecord) -> CandidateDetails:
        """Generate candidate details using LLM"""
        try:
            # Extract additional experience-related fields from Zoho data
            all_fields = employee_record.all_other_fields
            current_experience = all_fields.get("Current Experience", "")
            expertise = all_fields.get("Ask me about/Expertise", "")
            about_me = all_fields.get("About Me", "")
            date_of_joining = all_fields.get("Date of Joining", "")
            employment_type = all_fields.get("Employment Type", "")
            
            # Prepare comprehensive prompt with employee data
            employee_data_str = f"""
            Employee Information:
            - Name: {employee_record.name}
            - Job Title: {employee_record.job_title}
            - Department: {employee_record.department}
            - Current Experience: {current_experience}
            - Date of Joining: {date_of_joining}
            - Employment Type: {employment_type}
            - Expertise/Skills: {expertise}
            - About Me: {about_me}
            - Contact: {employee_record.contact_info}
            """
            
            prompt = f"""
            Based on the following employee information from Zoho People, generate a comprehensive candidate profile for talent management:
            
            {employee_data_str}
            
            Please provide a response in the following JSON format (respond only with valid JSON, no additional text):
            {{
                "profile": "A professional profile summary in 2-3 sentences based on their role, experience, and expertise",
                "skills": "Comma-separated list of relevant skills based on job title, expertise field, and experience",
                "experience": "Experience summary based on Current Experience, Date of Joining, and job history - be specific about years and roles",
                "summary": "Overall candidate summary in 3-4 sentences incorporating their experience level, skills, and career progression"
            }}
            
            Make sure to use the actual experience data provided (Current Experience: {current_experience}) and be specific about their tenure and expertise.
            Make sure your response is valid JSON only.
            """
            
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            content = response.content.strip() if response.content else ""
            
            logger.info(f"LLM raw response for {employee_record.employee_id}: {content[:200]}...")
            
            # Parse LLM response with improved error handling
            try:
                import json
                import re
                
                # Clean up the response - remove any markdown formatting
                cleaned_content = content
                if content.startswith('```json'):
                    # Remove markdown code blocks
                    cleaned_content = re.sub(r'^```json\s*', '', content)
                    cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
                elif content.startswith('```'):
                    # Remove any code blocks
                    cleaned_content = re.sub(r'^```[a-z]*\s*', '', content)
                    cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
                
                # Try to find JSON in the response if it's mixed with other text
                json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
                if json_match:
                    cleaned_content = json_match.group()
                
                parsed_response = json.loads(cleaned_content)
                
                skills_list = []
                if isinstance(parsed_response.get("skills"), str):
                    skills_list = [skill.strip() for skill in parsed_response["skills"].split(",")]
                elif isinstance(parsed_response.get("skills"), list):
                    skills_list = parsed_response["skills"]
                
                candidate_details = CandidateDetails(
                    candidate_id=f"cand_{employee_record.employee_id}",
                    employee_id=employee_record.employee_id,
                    name=employee_record.name,
                    email=employee_record.contact_info.get("email") if employee_record.contact_info.get("email") else f"employee_{employee_record.employee_id}@company.internal",
                    location=employee_record.contact_info.get("address", "Not specified"),
                    profile=parsed_response.get("profile", ""),
                    skills=skills_list,
                    experience=parsed_response.get("experience", ""),
                    summary=parsed_response.get("summary", ""),
                    generated_at=datetime.utcnow()
                )
                
            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                logger.warning(f"Failed to parse LLM JSON response for {employee_record.employee_id}, using fallback format: {e}")
                logger.warning(f"Raw LLM response was: {content}")
                
                # Enhanced fallback: use actual Zoho experience data
                all_fields = employee_record.all_other_fields
                current_experience = all_fields.get("Current Experience", "")
                date_of_joining = all_fields.get("Date of Joining", "")
                expertise = all_fields.get("Ask me about/Expertise", "")
                
                profile = f"Professional with experience in {employee_record.job_title} role"
                skills = [employee_record.job_title, employee_record.department] if employee_record.job_title else []
                
                # Add expertise skills if available
                if expertise:
                    expertise_skills = [skill.strip() for skill in expertise.split(",") if skill.strip()]
                    skills.extend(expertise_skills[:5])  # Limit to 5 additional skills
                
                # Use actual experience data if available
                if current_experience:
                    experience = f"Has {current_experience} of professional experience"
                    if date_of_joining:
                        experience += f", joined company on {date_of_joining}"
                    if employee_record.department:
                        experience += f" in {employee_record.department} department"
                else:
                    experience = f"Experience in {employee_record.department} department" if employee_record.department else "Professional experience"
                
                summary = f"{employee_record.name} is a {employee_record.job_title}"
                if current_experience:
                    summary += f" with {current_experience} of experience"
                if employee_record.department:
                    summary += f" in {employee_record.department}"
                if not summary.endswith("."):
                    summary += "."
                
                # Try to extract some info from the raw response if available
                if content:
                    # Simple heuristic to extract profile information
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 20:  # Likely a meaningful description
                            if 'profile' not in locals() or len(line) > len(profile):
                                profile = line[:200]  # Limit length
                            break
                
                candidate_details = CandidateDetails(
                    candidate_id=f"cand_{employee_record.employee_id}",
                    employee_id=employee_record.employee_id,
                    name=employee_record.name,
                    email=employee_record.contact_info.get("email") if employee_record.contact_info.get("email") else f"employee_{employee_record.employee_id}@company.internal",
                    location=employee_record.contact_info.get("address", "Not specified"),
                    profile=profile,
                    skills=skills,
                    experience=experience,
                    summary=summary,
                    generated_at=datetime.utcnow()
                )
            
            logger.info(f"Generated candidate details for employee: {employee_record.employee_id}")
            return candidate_details
            
        except Exception as e:
            logger.error(f"Failed to generate candidate details for employee {employee_record.employee_id}: {e}")
            # Create basic candidate details as fallback using actual Zoho data
            all_fields = employee_record.all_other_fields
            current_experience = all_fields.get("Current Experience", "")
            
            experience_text = "Experience information unavailable"
            if current_experience:
                experience_text = f"Has {current_experience} of professional experience"
            
            return CandidateDetails(
                candidate_id=f"cand_{employee_record.employee_id}",
                employee_id=employee_record.employee_id,
                name=employee_record.name,
                email=employee_record.contact_info.get("email") if employee_record.contact_info.get("email") else f"employee_{employee_record.employee_id}@company.internal",
                location=employee_record.contact_info.get("address", "Not specified"),
                profile=f"Employee: {employee_record.name}",
                skills=[employee_record.job_title] if employee_record.job_title else [],
                experience=experience_text,
                summary=f"Basic profile for {employee_record.name}" + (f" with {current_experience} experience" if current_experience else ""),
                generated_at=datetime.utcnow()
            )

    async def store_candidate_details(self, candidate_details: CandidateDetails) -> bool:
        """Store candidate details if not already exists"""
        try:
            # Check if candidate already exists by employee_id
            existing = await self.candidates_collection.find_one(
                {"employee_id": candidate_details.employee_id}
            )
            
            if existing:
                logger.info(f"Candidate details already exist for employee: {candidate_details.employee_id}")
                return False
            
            # Check if email already exists (if email is provided and not a generated internal email)
            if candidate_details.email and not candidate_details.email.endswith("@company.internal"):
                existing_email = await self.candidates_collection.find_one(
                    {"email": candidate_details.email}
                )
                if existing_email:
                    logger.warning(f"Candidate with email {candidate_details.email} already exists, updating employee_id reference")
                    # Update existing record to include this employee_id in some way, or skip
                    return False
            
            # Insert new candidate details
            result = await self.candidates_collection.insert_one(
                candidate_details.model_dump(by_alias=True, exclude={"id"})
            )
            
            logger.info(f"Stored candidate details for employee: {candidate_details.employee_id}")
            return True
            
        except Exception as e:
            # Handle duplicate key error specifically
            if "E11000" in str(e) and "email" in str(e):
                logger.warning(f"Duplicate email constraint violated for employee {candidate_details.employee_id}, skipping")
                return False
            logger.error(f"Failed to store candidate details for employee {candidate_details.employee_id}: {e}")
            return False

    async def update_sync_status(self, processed_employee_ids: List[str], error: Optional[str] = None):
        """Update sync status in database"""
        try:
            sync_status = SyncStatus(
                last_sync_time=datetime.utcnow(),
                sync_interval=self.sync_interval,
                access_token=self.zoho_access_token,
                processed_employee_ids=processed_employee_ids,
                last_error=error
            )
            
            # Upsert sync status (should only be one record)
            await self.sync_status_collection.replace_one(
                {},  # Empty filter to match any document
                sync_status.model_dump(by_alias=True, exclude={"id"}),
                upsert=True
            )
            
            logger.info(f"Updated sync status. Processed {len(processed_employee_ids)} employees")
            
        except Exception as e:
            logger.error(f"Failed to update sync status: {e}")

    async def run_sync(self) -> Dict[str, Any]:
        """Run a single sync operation"""
        sync_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "employees_fetched": 0,
            "employees_processed": 0,
            "candidates_created": 0,
            "errors": []
        }
        
        try:
            logger.info("Starting Zoho sync operation")
            
            # Fetch employees from Zoho
            employees_data = await self.fetch_employees_from_zoho()
            sync_result["employees_fetched"] = len(employees_data)
            
            processed_employee_ids = []
            candidates_created = 0
            
            # Process each employee
            for employee_data in employees_data:
                try:
                    # Store employee record
                    employee_record = await self.store_employee(employee_data)
                    
                    # Generate and store candidate details
                    candidate_details = await self.generate_candidate_details_with_llm(employee_record)
                    candidate_stored = await self.store_candidate_details(candidate_details)
                    
                    if candidate_stored:
                        candidates_created += 1
                    
                    processed_employee_ids.append(employee_record.employee_id)
                    
                except Exception as e:
                    error_msg = f"Failed to process employee {employee_data.get('Employeeid', 'unknown')}: {e}"
                    logger.error(error_msg)
                    sync_result["errors"].append(error_msg)
            
            sync_result["employees_processed"] = len(processed_employee_ids)
            sync_result["candidates_created"] = candidates_created
            
            # Update sync status
            await self.update_sync_status(processed_employee_ids)
            
            logger.info(f"Sync completed. Processed {len(processed_employee_ids)} employees, created {candidates_created} candidates")
            
        except Exception as e:
            error_msg = f"Sync operation failed: {e}"
            logger.error(error_msg)
            sync_result["errors"].append(error_msg)
            await self.update_sync_status([], error_msg)
        
        return sync_result

    async def start_periodic_sync(self):
        """Start periodic sync based on configured interval"""
        logger.info(f"Starting periodic sync with {self.sync_interval} minute interval")
        
        while True:
            try:
                await self.run_sync()
                
                # Wait for next sync
                wait_seconds = self.sync_interval * 60
                logger.info(f"Waiting {wait_seconds} seconds until next sync")
                await asyncio.sleep(wait_seconds)
                
            except Exception as e:
                logger.error(f"Error in periodic sync: {e}")
                # Wait a shorter time before retrying on error
                await asyncio.sleep(60)

    async def get_all_candidates(self) -> List[Dict[str, Any]]:
        """Retrieve all candidate details"""
        try:
            cursor = self.candidates_collection.find({})
            candidates = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                doc["_id"] = str(doc["_id"])
                candidates.append(doc)
            
            logger.info(f"Retrieved {len(candidates)} candidate records")
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to retrieve candidates: {e}")
            return []

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")