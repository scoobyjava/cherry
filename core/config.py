import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """🚀 Central Configuration for Cherry AI"""

    # --- Application Metadata ---
    APP_NAME = "Cherry AI"
    VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # --- Server Configuration ---
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # --- Public URL Configuration ---
    CODESPACES_PUBLIC_URL = os.getenv("CODESPACES_PUBLIC_URL", f"http://localhost:{PORT}")

    # --- API Keys ---
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN", "")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    GCP_PROJECT_NUMBER = os.getenv("GCP_PROJECT_NUMBER", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN", "")
    VENICE_API_KEY = os.getenv("VENICE_API_KEY", "")

    # --- LLM Model Settings ---
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")
    FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-3.5-turbo")

    # --- Vector Database (ChromaDB) Settings ---
    CHROMADB_PERSIST_DIRECTORY = os.getenv("CHROMADB_PERSIST_DIRECTORY", "./chroma_db")

    # --- Agent Enablement Flags ---
    ENABLE_RESEARCH_AGENT = os.getenv("ENABLE_RESEARCH_AGENT", "True").lower() == "true"
    ENABLE_CREATIVE_AGENT = os.getenv("ENABLE_CREATIVE_AGENT", "True").lower() == "true"
    ENABLE_CODE_AGENT = os.getenv("ENABLE_CODE_AGENT", "True").lower() == "true"
    ENABLE_ANALYTICS_AGENT = os.getenv("ENABLE_ANALYTICS_AGENT", "True").lower() == "true"

    # --- Logging Configuration ---
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "cherry_ai.log")

    # --- Storage & Database Settings (just added back!) ---
    DB_TYPE = os.getenv("DB_TYPE", "memory")
    DB_URL = os.getenv("DB_URL", "")

    # --- Task Management Settings (just added back!) ---
    MAX_PENDING_TASKS = int(os.getenv("MAX_PENDING_TASKS", 100))
    MAX_COMPLETED_TASKS = int(os.getenv("MAX_COMPLETED_TASKS", 1000))
    TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", 300))

    # --- External Service URLs (just added back!) ---
    SERVICE_ENDPOINTS = {
        "knowledge_base": os.getenv("KNOWLEDGE_BASE_URL", ""),
        "user_profile_service": os.getenv("USER_PROFILE_SERVICE_URL", ""),
        "notification_service": os.getenv("NOTIFICATION_SERVICE_URL", "")
    }
