# backend/core/indexing_service.py
import base64
import spacy
from sentence_transformers import SentenceTransformer
import chromadb
from backend.db.database import SessionLocal
from backend.db import models

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
        Takes raw email data, processes it, and stores the results.
        """
        # 1. Decode the email body (it comes from Google in base64)
        if 'parts' in email_data['payload']:
            part = email_data['payload']['parts'][0]
            if 'data' in part['body']:
                body_data = part['body']['data']
                decoded_body = base64.urlsafe_b64decode(body_data).decode('utf-8')
            else:
                decoded_body = "" # Handle emails with no body
        else:
            decoded_body = ""

        # 2. Extract Metadata
        headers = email_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'No Sender')

        # 3. Perform NLP Analysis
        doc = self.nlp(decoded_body[:100000]) # Process first 100k chars
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # 4. Create Vector Embedding
        # We'll vectorize the most important parts: subject and a snippet of the body
        text_to_vectorize = f"Subject: {subject}\n\n{email_data['snippet']}"
        embedding = self.vector_model.encode(text_to_vectorize).tolist()

        # 5. Store the results
        # Store metadata in SQLite
        db_email = models.Email(
            id=email_data['id'],
            thread_id=email_data['threadId'],
            sender=sender,
            subject=subject,
            snippet=email_data['snippet']
        )
        self.db.add(db_email)
        self.db.commit()

        # Store vector in ChromaDB
        self.collection.add(
            embeddings=[embedding],
            metadatas=[{"sender": sender, "subject": subject}], # Metadata for filtering later
            ids=[email_data['id']]
        )

        print(f"✅ Indexed email from {sender} | Subject: {subject}")
        if entities:
            print(f"   -> Found entities: {entities[:3]}") # Print first 3 found entities

# Create a single instance
indexing_service = IndexingService()