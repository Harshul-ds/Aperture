# backend/api/jobs.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import SessionLocal
from backend.db import models
from backend.models.job import JobApplicationResponse, JobApplicationItem

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/", 
    response_model=JobApplicationResponse, 
    summary="Get all job application emails"
)
def get_job_applications(db: Session = Depends(get_db)):
    """
    Retrieves all emails that have been classified as 'Job Application',
    along with their extracted company and status.
    """
    db_jobs = db.query(models.Email).filter(models.Email.category == "Job Application").all()
    
    # Map the SQLAlchemy models to the Pydantic models
    job_items = [
        JobApplicationItem(
            id=job.id,
            sender=job.sender,
            subject=job.subject,
            company=job.job_company,
            status=job.job_status
        )
        for job in db_jobs
    ]

    return JobApplicationResponse(status="success", results=job_items)
