# backend/api/search.py
from fastapi import APIRouter, Depends
from backend.models.search import SearchResponse
from backend.core.search_service import SearchService, search_service

# Create an API router
router = APIRouter()

@router.get(
    "/", # The path will be relative to the prefix in main.py, so this becomes /search/
    response_model=SearchResponse,
    summary="Perform a search query"
)
def search(
    q: str,
    service: SearchService = Depends(lambda: search_service)
):
    """
    Takes a search query `q` and returns a list of relevant results
    from the user's indexed data.
    """
    return service.find_results(query=q)