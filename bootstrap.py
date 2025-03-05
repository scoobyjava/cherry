import threading
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config
from cherry.core.orchestrator import AdvancedOrchestrator
from api import setup_routes
from logger import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title=Config.APP_NAME,
        description="🍒 Autonomous AI assistant",
        version=Config.VERSION,
        debug=Config.DEBUG
    )
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    return app

def initialize_orchestrator() -> AdvancedOrchestrator:
    orchestrator = AdvancedOrchestrator()
    orchestrator_thread = threading.Thread(target=orchestrator.run, daemon=True)
    orchestrator_thread.start()
    orchestrator._thread = orchestrator_thread
    return orchestrator

async def bootstrap_async_function():
    try:
        logger.info("Bootstrapping Cherry AI...")
        app = create_app()
        orch = initialize_orchestrator()
        setup_routes(app, orch)
        await asyncio.sleep(1)
        @app.on_event("shutdown")
        async def shutdown():
            orch.stop()
            orch._thread.join(timeout=5.0)
        return app
    except asyncio.CancelledError:
        print("Task was cancelled")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")

import threading
import time
import logging
from typing import Optional

from cherry.core.orchestrator import Orchestrator
from config import Config
from logger import setup_logger

class CherrySystem:
    """Main Cherry AI system wrapper that manages initialization and components."""
    
    def __init__(self, config_path: Optional[str] = None):
        # Initialize configuration
        self.config = Config(config_path) if config_path else Config()
        
        # Setup logging
        self.logger = setup_logger("cherry_system", log_level=self.config.log_level)
        self.logger.info("Initializing Cherry AI system...")
        
        # Initialize memory system
        self._init_memory()
        
        # Initialize orchestrator
        self.orchestrator = Orchestrator(self.config, self.memory)
        self.orchestrator_thread = None
        self.is_running = False

    def _init_memory(self):
        """Initialize the memory subsystem based on configuration."""
        try:
            from memory_chroma import ChromaMemory
            self.memory = ChromaMemory(self.config)
            self.logger.info("Initialized Chroma memory system")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory system: {str(e)}")
            raise

    def start(self):
        """Start the Cherry AI system and orchestrator in a background thread."""
        if self.is_running:
            self.logger.warning("Cherry AI system is already running")
            return
        
        def orchestrator_worker():
            self.logger.info("Starting orchestrator in background thread")
            self.orchestrator.run()
        
        self.orchestrator_thread = threading.Thread(
            target=orchestrator_worker,
            daemon=True
        )
        self.orchestrator_thread.start()
        self.is_running = True
        self.logger.info("Cherry AI system started successfully")
    
    def stop(self):
        """Stop the Cherry AI system and orchestrator."""
        if not self.is_running:
            self.logger.warning("Cherry AI system is not running")
            return
        
        self.logger.info("Stopping Cherry AI system...")
        self.orchestrator.stop()
        
        # Wait for orchestrator thread to finish
        if self.orchestrator_thread and self.orchestrator_thread.is_alive():
            self.orchestrator_thread.join(timeout=5.0)
            
        self.is_running = False
        self.logger.info("Cherry AI system stopped")
    
    def status(self):
        """Return the current status of the Cherry AI system."""
        return {
            "running": self.is_running,
            "orchestrator_active": self.orchestrator_thread.is_alive() if self.orchestrator_thread else False,
            "memory_status": self.memory.status() if hasattr(self.memory, "status") else "unknown"
        }


# Singleton instance of the Cherry system
_cherry_instance = None

def get_cherry_system(config_path: Optional[str] = None) -> CherrySystem:
    """Get or create the singleton instance of the Cherry AI system."""
    global _cherry_instance
    if _cherry_instance is None:
        _cherry_instance = CherrySystem(config_path)
    return _cherry_instance

def initialize_cherry(config_path: Optional[str] = None) -> CherrySystem:
    """Initialize the Cherry AI system and return the instance."""
    cherry = get_cherry_system(config_path)
    cherry.start()
    return cherry
