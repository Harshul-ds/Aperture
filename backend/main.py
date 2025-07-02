# backend/main.py

import uvicorn
import asyncio
from pydantic import PydanticDeprecatedSince20
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from anyio import to_thread
from backend.api.logger import manager as log_manager

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import logging
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.FATAL)

from backend.core.logging_setup import configure_logging
configure_logging()

from backend.db.migrate import run_migrations
from backend.api import search, auth, ingest, jobs, logger
from backend.core.config import settings
from backend.core.ingestion_service import ingestion_service
from backend.core.auth_service import get_user_credentials, build_google_service

# This runs once when the application starts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block runs on application startup
    print("--- Aperture Backend starting up ---")
    
    log_manager.set_main_loop()

    # Ensure database schema exists before handling requests
    run_migrations()

    async def startup_ingestion_task():
        # Wait a few seconds for the server to be fully ready
        await asyncio.sleep(5)
        print("--- Checking for new emails in the background ---")
        
        creds = get_user_credentials() # This function must exist in your auth_service
        if creds:
            try:
                service = build_google_service(creds) # This function must exist in your auth_service
                await to_thread.run_sync(ingestion_service.fetch_and_process_emails, 50)
                print("--- Background email check complete ---")
            except Exception as e:
                print(f"--- Background ingestion failed: {e} ---")
        else:
            print("--- No valid credentials found, skipping startup ingestion. Please authenticate. ---")

    # Create the background task so it doesn't block the server from starting
    asyncio.create_task(startup_ingestion_task())
    
    yield
    # This block runs on application shutdown
    print("--- Aperture Backend shutting down ---")

# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan # Use our new startup/shutdown manager
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["Ingestion"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(logger.router, prefix="/api/v1/log", tags=["Logging"])

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": f"Welcome to {settings.APP_NAME} v{app.version}"}