# backend/models/job.py
from pydantic import BaseModel
from typing import List, Optional

class JobApplicationItem(BaseModel):
    """Defines the structure of a single job application email."""
    id: str
    sender: str
    subject: str
    company: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class JobApplicationResponse(BaseModel):
    """Defines the structure of the job applications API response."""
    status: str
    results: List[JobApplicationItem]
