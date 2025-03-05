from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
DATABASE_URL = config('DATABASE_URL')

LLM_CONFIG = {
    "llms": ["LLMAdapter1", "LLMAdapter2"]
}

# Configuration for external services
SPOTIFY_API_KEY = 'your_spotify_api_key'
SMART_HOME_API_KEY = 'your_smart_home_api_key'

# Pinecone settings for vector database
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX", "default")

# PostgreSQL settings for archiving vectors
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")

# Vector archiving settings
ARCHIVE_AGE_MONTHS = int(os.environ.get("ARCHIVE_AGE_MONTHS", 6))
ARCHIVE_BATCH_SIZE = int(os.environ.get("ARCHIVE_BATCH_SIZE", 100))
ARCHIVE_SCHEDULE_TIME = os.environ.get("ARCHIVE_SCHEDULE_TIME", "02:00")

# Pinecone configuration
PINECONE_API_KEY = "your-api-key"
PINECONE_ENVIRONMENT = "your-environment"
PINECONE_INDEX_NAME = "memory-index"

# PostgreSQL database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "memories_db",
    "user": "postgres",
    "password": "your-password",
    "port": 5432
}
