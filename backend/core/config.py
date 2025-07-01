# backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Manages application-wide settings."""
    APP_NAME: str = "Aperture Backend"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    class Config:
        # This tells pydantic-settings to look for a .env file
        env_file = ".env"

# Create a single, importable instance of the settings
settings = Settings()