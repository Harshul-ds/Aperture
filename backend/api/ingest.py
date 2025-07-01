# backend/api/ingest.py
from fastapi import APIRouter, Depends, BackgroundTasks
from backend.core.ingestion_service import IngestionService, ingestion_service

router = APIRouter()

def run_ingestion(service: IngestionService):
    """The actual function that the background task will run."""
    print("Background ingestion task started...")
    emails = service.fetch_and_process_emails()
    if emails:
        print(f"Successfully fetched {len(emails)} emails.")
        # In the future, we will save these emails to our local database here.
        for email in emails:
            print(f"  - Subject: {email['subject']}")
    else:
        print("Ingestion task finished with no new emails.")


@router.post("/gmail", summary="Start Gmail Ingestion")
def trigger_gmail_ingestion(
    background_tasks: BackgroundTasks,
    service: IngestionService = Depends(lambda: ingestion_service)
):
    """
    Triggers the process of fetching the latest Gmail messages in the background.
    """
    print("Received request to start Gmail ingestion.")
    background_tasks.add_task(run_ingestion, service)
    return {"status": "success", "message": "Gmail ingestion process started in the background."}