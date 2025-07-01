# backend/core/indexing_service.py
import base64
import spacy
from sentence_transformers import SentenceTransformer
import chromadb
from backend.db.database import SessionLocal
from backend.db import models
from backend.core.classification_service import classification_service

class IndexingService:
    def __init__(self):
        # Load models once and reuse them.
        print("Loading NLP and Vector models...")
        self.nlp = spacy.load("en_core_web_sm")
        self.vector_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Models loaded.")

        # Connect to ChromaDB
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(name="emails")
        
        # Get a database session
        self.db = SessionLocal()

    def process_and_index_email(self, email_data: dict):
        """
        Takes raw email data, processes it, and stores the results, including attachments.
        """
        # Check if email is already indexed
        if self.db.query(models.Email).filter(models.Email.id == email_data['id']).first():
            print(f"Skipping already indexed email: {email_data['id']}")
            return

        # 1. Decode the email body
        decoded_body = ""
        if 'parts' in email_data['payload']:
            for part in email_data['payload']['parts']:
                if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                    body_data = part['body']['data']
                    decoded_body = base64.urlsafe_b64decode(body_data).decode('utf-8', 'ignore')
                    break # Stop after finding the first plain text part
        
        # 2. Extract Metadata
        headers = email_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'No Sender')

        # 3. Perform NLP Analysis
        doc = self.nlp(decoded_body[:100000])
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # 4. Create Vector Embedding
        text_to_vectorize = f"Subject: {subject}\n\n{email_data['snippet']}"
        embedding = self.vector_model.encode(text_to_vectorize).tolist()

        # 5a. Classify the email
        category = classification_service.classify_email(subject, decoded_body)

        # 5. Store Email and Attachments in SQLite
        db_email = models.Email(
            id=email_data['id'],
            thread_id=email_data['threadId'],
            sender=sender,
            subject=subject,
            snippet=email_data['snippet'],
            category=category
        )

        # 6. Check for and store attachments
        if 'parts' in email_data['payload']:
            for part in email_data['payload']['parts']:
                if part.get('filename'):
                    new_attachment = models.Attachment(
                        filename=part['filename'],
                        mime_type=part.get('mimeType', 'application/octet-stream'),
                        size=part['body'].get('size', 0)
                    )
                    db_email.attachments.append(new_attachment)
                    print(f"   -> Found attachment: {part['filename']}")

        self.db.add(db_email)
        self.db.commit()

        # 7. Store vector in ChromaDB
        self.collection.add(
            embeddings=[embedding],
            metadatas=[{"sender": sender, "subject": subject}],
            ids=[email_data['id']]
        )

        print(f"✅ Indexed email from {sender} | Subject: {subject}")
        if entities:
            print(f"   -> Found entities: {entities[:3]}")

# Create a single instance
indexing_service = IndexingService()