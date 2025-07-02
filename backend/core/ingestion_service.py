# backend/core/ingestion_service.py

import logging
from datetime import datetime, timezone
from typing import Optional
import googleapiclient.discovery
import base64

# Core application imports
from backend.db.database import SessionLocal
from backend.db import models
from backend.core.auth_service import get_user_credentials, build_google_service
from backend.core.classification_service import classification_service

# All required libraries
from sentence_transformers import SentenceTransformer
import spacy
import chromadb
from chromadb.config import Settings as ChromaSettings

class IngestionService:
    """A unified service for all ingestion, processing, and indexing."""
    def __init__(self):
        logging.info("Initializing IngestionService (Unified)...")
        # --- All necessary clients and models are loaded here ---
        self.nlp = spacy.load("en_core_web_sm")
        self.vector_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(name="emails")
        logging.info("IngestionService initialized successfully.")

    def get_latest_email_date(self) -> Optional[datetime]:
        # ... (implementation is correct, no changes needed)
        db = SessionLocal()
        try:
            latest_email = db.query(models.Email).order_by(models.Email.received_at.desc()).first()
            if latest_email: return latest_email.received_at
            return None
        finally: db.close()

    def fetch_and_process_emails(self, limit: int = 50):
        # ... (the full, correct implementation from our last exchange goes here) ...
        # This is the function that fetches from Gmail, processes,
        # vectorizes, and saves to both databases.
        logging.info("Starting email fetch and process cycle...")
        creds = get_user_credentials()
        if not creds:
            logging.error("INGESTION FAILED: No valid credentials found.")
            return

        service = build_google_service(creds)
        latest_date = self.get_latest_email_date()
        gmail_query = "category:primary"
        if latest_date: gmail_query += f" after:{int(latest_date.timestamp())}"

        logging.info(f"Querying Gmail API with: '{gmail_query}'")
        results = service.users().messages().list(userId='me', q=gmail_query, maxResults=limit).execute()
        messages = results.get('messages', [])

        if not messages:
            logging.info("No new messages found to ingest.")
            return

        db = SessionLocal()
        processed_in_this_batch = set()
        try:
            for i, message_summary in enumerate(messages):
                email_id = message_summary['id']
                if email_id in processed_in_this_batch: continue
                if db.query(models.Email).filter(models.Email.id == email_id).first(): continue
                
                logging.info(f"Processing message {i+1}/{len(messages)} (ID: {email_id})")
                email_data = service.users().messages().get(userId='me', id=email_id, format='full').execute()
                
                headers = email_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'No Sender')
                date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                try: received_at_dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z').astimezone(timezone.utc)
                except (ValueError, TypeError): received_at_dt = datetime.now(timezone.utc)

                body_text = ""
                if 'parts' in email_data['payload']:
                    for part in email_data['payload']['parts']:
                        if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                            body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', 'ignore'); break
                
                text_to_vectorize = f"Subject: {subject}\n\n{email_data['snippet']}"
                embedding = self.vector_model.encode(text_to_vectorize).tolist()
                
                classification_results = classification_service.classify_email(subject, body_text)
                db_email = models.Email(id=email_id, thread_id=email_data['threadId'], sender=sender, subject=subject, snippet=email_data['snippet'], received_at=received_at_dt, category=classification_results.get('category', 'General'), job_company=classification_results.get('company'), job_status=classification_results.get('status', 'Applied' if classification_results.get('category') == 'Job Application' else None))
                
                has_attachments = False
                if 'parts' in email_data['payload']:
                    for part in email_data['payload']['parts']:
                        if part.get('filename'):
                            has_attachments = True
                            db_email.attachments.append(models.Attachment(filename=part['filename'], mime_type=part.get('mimeType', 'application/octet-stream'), size=part['body'].get('size', 0)))
                
                db.add(db_email)
                self.collection.add(ids=[email_id], embeddings=[embedding], metadatas=[{"sender": sender, "subject": subject, "has_attachment": has_attachments}])
                processed_in_this_batch.add(email_id)

            db.commit()
            logging.info(f"SUCCESS: Committed {len(processed_in_this_batch)} unique emails to the database.")

        except Exception as e:
            logging.error(f"DATABASE ERROR: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

# The singleton instance that the rest of the app will use
ingestion_service = IngestionService()
