# backend/models/search.py
from pydantic import BaseModel
from typing import List

class SearchResultItem(BaseModel):
    """Defines the structure of a single search result item."""
    id: str
    sender: str
    subject: str
    preview: str
    relevance_score: float
    has_attachment: bool
    category: str

class SearchResponse(BaseModel):
    """Defines the structure of the entire search API response."""
    status: str
    query: str
    results: List[SearchResultItem]