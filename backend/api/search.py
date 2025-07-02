# backend/api/search.py

import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List

# --- KEY CHANGE: Import the correct, unified service ---
from backend.core.ingestion_service import ingestion_service
from backend.db.database import SessionLocal
from backend.db import models

router = APIRouter()

class SearchResultItem(BaseModel):
    id: str; sender: str; subject: str
    preview: str = Field(..., alias="snippet")
    relevance_score: float = Field(..., alias="distance")
    category: str; has_attachment: bool = Field(default=False)
    class Config: allow_population_by_field_name = True

class SearchResponse(BaseModel):
    status: str = "success"; results: List[SearchResultItem]

@router.get("/", response_model=SearchResponse, summary="Search emails via vector search")
def search_emails(query: str = Query(..., min_length=2)):
    """
    UPGRADED Search Implementation:
    1. Queries ChromaDB for initial semantic candidates.
    2. Enriches results with full data from the SQL database.
    3. (Future enhancement) Could add a re-ranking step here.
    """
    logging.info(f"Received search query: '{query}'")
    
    # --- KEY CHANGE: Use the collection from our unified service ---
    collection = ingestion_service.collection
    if collection.count() == 0: return SearchResponse(results=[])

    try:
        # Step 1: Get top results from ChromaDB
        chroma_results = collection.query(
            query_texts=[query],
            n_results=20, # Get a slightly larger pool of candidates
            include=["metadatas", "documents", "distances"]
        )
        
        email_ids = chroma_results['ids'][0]
        if not email_ids: return SearchResponse(results=[])

        # Step 2: Enrich with SQL data
        db = SessionLocal()
        try:
            sql_emails_dict = {email.id: email for email in db.query(models.Email).filter(models.Email.id.in_(email_ids)).all()}
        finally:
            db.close()

        # Step 3: Combine and format results
        formatted_results = []
        for i in range(len(email_ids)):
            email_id = email_ids[i]
            if email_id in sql_emails_dict:
                sql_email = sql_emails_dict[email_id]
                formatted_results.append(SearchResultItem(
                    id=email_id,
                    distance=chroma_results['distances'][0][i],
                    snippet=chroma_results['documents'][0][i],
                    sender=sql_email.sender,
                    subject=sql_email.subject,
                    category=sql_email.category,
                    has_attachment=len(sql_email.attachments) > 0
                ))
        
        # Here you could add a re-ranking model in the future to improve this sort order
        # For now, we sort by the distance score from ChromaDB (lower is better)
        formatted_results.sort(key=lambda x: x.relevance_score)
        
        return SearchResponse(results=formatted_results[:15]) # Return the top 15 after sorting

    except Exception as e:
        logging.error(f"Error during search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during search.")
    