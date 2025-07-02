# backend/api/jobs.py (Corrected Version)

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.db.database import SessionLocal
from backend.db import models

router = APIRouter()

# --- Pydantic Models for the API Response ---
class JobResultItem(BaseModel):
    id: str
    company: Optional[str] = "Unknown Company"
    subject: str
    # --- THE DEFINITIVE FIX ---
    # The field name here MUST match the data source (models.Email.job_status)
    job_status: str = Field(alias="status") 

    class Config:
        # This allows us to still output 'status' in the JSON
        # while using 'job_status' in our Python code.
        allow_population_by_field_name = True 
        
class JobsResponse(BaseModel):
    status: str = "success"
    results: List[JobResultItem]

@router.get("/", response_model=JobsResponse, summary="Get all job-related emails")
def get_job_applications():
    logging.info("Fetching job application data from SQL database...")
    db = SessionLocal()
    try:
        job_categories = ['Applied', 'Interview', 'Offer', 'Rejected', 'Job Application']
        
        job_emails = db.query(models.Email).filter(
            models.Email.job_status.in_(job_categories)
        ).all()

        # This mapping will now work correctly because the field names match.
        results = [
            JobResultItem(
                id=email.id,
                company=email.job_company,
                subject=email.subject,
                job_status=email.job_status # Now maps to the correct field
            ) for email in job_emails
        ]
        return JobsResponse(results=results)
    except Exception as e:
        logging.error(f"Error fetching job data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching job data.")
    finally:
        db.close()