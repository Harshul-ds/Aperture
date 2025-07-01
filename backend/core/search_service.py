# backend/core/search_service.py
from backend.models.search import SearchResponse, SearchResultItem

class SearchService:
    def find_results(self, query: str) -> SearchResponse:
        """
        Performs the search logic.
        In the future, this will query ChromaDB. For now, it returns mock data.
        """
        print(f"Core logic received search for: '{query}'")

        # Simulate database results
        mock_results = [
            SearchResultItem(id="1", sender="elon@x.com", subject="Regarding our conversation", preview="Hey, let's connect about the...", relevance_score=0.92),
            SearchResultItem(id="2", sender="mom@family.com", subject="Vacation photos", preview="I've attached the photos from...", relevance_score=0.85),
            SearchResultItem(id="3", sender="project-manager@work.com", subject=f"Update on '{query}'", preview="Here is the latest update regarding your query...", relevance_score=0.95),
        ]

        return SearchResponse(status="success", query=query, results=mock_results)

# Create a single, importable instance of the service
search_service = SearchService()