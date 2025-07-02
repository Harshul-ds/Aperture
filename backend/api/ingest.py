# backend/api/ingest.py

import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from backend.core.ingestion_service import ingestion_service

router = APIRouter()

def run_ingestion_task():
    """
    This is the actual function the background task will run.
    It directly calls the method that does all the work.
    """
    try:
        logging.info("BACKGROUND TASK: Starting...")
        # We don't need to get a return value, we just need to call the function.
        ingestion_service.fetch_and_process_emails(limit=50)
        logging.info("BACKGROUND TASK: Finished successfully.")
    except Exception as e:
        logging.error(f"BACKGROUND TASK FAILED: {e}", exc_info=True)


@router.post("/gmail", summary="Start Gmail Ingestion")
def trigger_gmail_ingestion(background_tasks: BackgroundTasks):
    """
    Triggers the process of fetching the latest Gmail messages in the background.
    """
    logging.info("API ENDPOINT: Received request to start Gmail ingestion.")
    background_tasks.add_task(run_ingestion_task)
    return {"status": "success", "message": "Gmail ingestion process started in the background. Check terminal for progress."}