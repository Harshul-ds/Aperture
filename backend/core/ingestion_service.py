# backend/core/ingestion_service.py (Upgraded)
from googleapiclient.discovery import build
from backend.core.auth_service import auth_service
from backend.core.indexing_service import indexing_service # Import our new service

class IngestionService:
    def __init__(self):
        self.creds = auth_service.get_credentials()
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    def fetch_and_process_emails(self, max_results: int = 10):
        results = self.gmail_service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No new messages to process.")
            return

        for message in messages:
            # Get the FULL email data, not just the metadata
            msg = self.gmail_service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            
            # Pass the full email data to the indexing service to handle the rest
            indexing_service.process_and_index_email(msg)

# Create a single instance
ingestion_service = IngestionService()