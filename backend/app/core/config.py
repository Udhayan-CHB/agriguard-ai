"""
Configuration settings using pydantic-settings.
Reads from .env file and environment variables.
"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # Llama 3.2 3B runs locally through Ollama, needs no API key, and is much
    # more responsive on typical student laptops than Granite 3.1 8B.
    OLLAMA_MODEL: str = "llama3.2:3b"

    # # IBM Watson (optional)
    # WATSONX_API_KEY: str = ""
    # WATSONX_PROJECT_ID: str = ""
    # WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"

    # # Watson Discovery is optional. Keeping these inside Settings means an
    # # unconfigured installation cleanly falls back to local RAG knowledge.
    # WATSON_DISCOVERY_API_KEY: str = ""
    # WATSON_DISCOVERY_URL: str = "https://api.us-south.discovery.watson.cloud.ibm.com"
    # WATSON_DISCOVERY_PROJECT_ID: str = ""
    # WATSON_DISCOVERY_COLLECTION_ID: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./agriguard.db"

    # Chroma
    CHROMA_PERSIST_DIR: str = "../data/chroma_db"

    # API
    API_V1_STR: str = "/api/v1"
    MAX_CHAT_HISTORY: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

SECRET_KEY: str = "ce9ea915b402bf5dab392102d8bfb03718b9c803498cb84dd7c42e0dc28e4e59"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60