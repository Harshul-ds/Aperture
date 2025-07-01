# backend/core/search_service.py
import chromadb
from sentence_transformers import SentenceTransformer
from backend.models.search import SearchResponse, SearchResultItem
from backend.db.database import SessionLocal
from backend.db import models

class SearchService:
    def __init__(self):
        """
        Initializes the search service, loading the model and connecting to ChromaDB.
        """
        print("Loading Vector model for Search...")
        # Re-use the same model as the indexing service for consistent vectors
        self.vector_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded.")

        # Connect to the same ChromaDB instance and collection
        self.chroma_client = chromadb.Client()
        # Assumes the collection has already been created by the indexing service
        self.collection = self.chroma_client.get_collection(name="emails")

        # Get a database session for retrieving metadata from SQLite
        self.db = SessionLocal()

    def find_results(self, query: str) -> SearchResponse:
        """
        Performs a vector search against the ChromaDB collection
        and retrieves corresponding metadata from SQLite.
        """
        print(f"Core logic received search for: '{query}'")

        # 1. Create a vector embedding for the user's query
        query_embedding = self.vector_model.encode(query).tolist()

        # 2. Query ChromaDB to find the 10 most similar email IDs
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=10
            )
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return SearchResponse(status="error", query=query, results=[])

        if not results or not results.get('ids') or not results['ids'][0]:
            print("No results found in ChromaDB.")
            return SearchResponse(status="success", query=query, results=[])

        # 3. Retrieve email metadata from SQLite using the IDs from ChromaDB
        email_ids = results['ids'][0]
        distances = results['distances'][0]

        # Fetch all matching emails from SQLite in a single, efficient query
        db_emails = self.db.query(models.Email).filter(models.Email.id.in_(email_ids)).all()
        
        # Create a dictionary for quick lookups by ID
        email_map = {email.id: email for email in db_emails}

        # 4. Format the final results, combining data from both databases
        final_results = []
        for i, email_id in enumerate(email_ids):
            email_details = email_map.get(email_id)
            if email_details:
                # Convert ChromaDB's distance to a more intuitive relevance score (1 - distance)
                # A lower distance means more similar, so a higher score is better.
                relevance_score = 1 - distances[i]
                
                final_results.append(
                    SearchResultItem(
                        id=email_details.id,
                        sender=email_details.sender,
                        subject=email_details.subject,
                        preview=email_details.snippet, # Use the snippet from SQLite
                        relevance_score=round(relevance_score, 2),
                        has_attachment=True if email_details.attachments else False
                    )
                )

        return SearchResponse(status="success", query=query, results=final_results)

# Create a single, importable instance of the service
search_service = SearchService()
