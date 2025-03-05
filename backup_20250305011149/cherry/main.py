# main.py
import uvicorn
from bootstrap import bootstrap
from config import Config
from logger import logger
from cherry.memory.memory_system import MemorySystem
from agents.creative import CreativeAgent
import logging
from cherry.core.orchestrator import Orchestrator

# Create the FastAPI application instance
app = bootstrap()
memory = MemorySystem(db_path='your_database.db')
orchestrator = Orchestrator(memory)

def initialize_agents(config, memory):
    # Add CreativeAgent to the available agents
    agents = {
        "creative": CreativeAgent(config, memory)
    }
    
    return agents

def main():
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

    # Example usage of MemorySystem
    memory.set_context('user_name', 'Alice')
    user_name = memory.get_context('user_name')
    print(f'Hello, {user_name}!')

    # Example usage of Orchestrator
    orchestrator.coordinate()

    # Run the app with Uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT, reload=Config.DEBUG)

if __name__ == "__main__":
    main()
