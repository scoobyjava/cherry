# main.py
import uvicorn
from bootstrap import bootstrap
from config import Config
from logger import logger

# Create the FastAPI application instance
app = bootstrap()

if __name__ == "__main__":
    # Display environment status
    logger.info(f"🍒 Cherry AI v{Config.VERSION} starting up...")

    # Check for API keys
    api_keys = {
        "OpenAI": bool(Config.OPENAI_API_KEY),
        "Elevenlabs": bool(Config.ELEVENLABS_API_KEY),
        "Gemini": bool(Config.GEMINI_API_KEY),
        "Grok": bool(Config.GROK_API_KEY)
    }

    available_keys = [k for k, v in api_keys.items() if v]
    logger.info(f"🔑 Loaded API keys: {', '.join(available_keys) if available_keys else 'None'}")

    if not Config.OPENAI_API_KEY:
        logger.warning("⚠️ OpenAI API key not found. LLM functionality will be limited.")

    # Run the app with Uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT, reload=Config.DEBUG)
