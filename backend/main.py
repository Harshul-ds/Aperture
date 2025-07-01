# backend/main.py (The Correct, Final Version for this Step)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import create_db_and_tables

# --- KEY CHANGE: Import BOTH routers now ---
from backend.api import search, auth, ingest
from backend.core.config import settings

create_db_and_tables()
# Create the main FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)

# CORS Middleware allows our frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- KEY CHANGE: Include BOTH routers ---
# This makes the /auth/google endpoint available to the application
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(search.router, prefix="/search", tags=["Search"])


@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "ok", "message": f"Welcome to {settings.APP_NAME}"}


# This block is for running the server directly during development
if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT)