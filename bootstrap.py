import threading
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

def bootstrap() -> FastAPI:
    logger.info("Bootstrapping Cherry AI...")
    app = create_app()
    orch = initialize_orchestrator()
    setup_routes(app, orch)

    @app.on_event("shutdown")
    async def shutdown():
        orch.stop()
        orch._thread.join(timeout=5.0)

    return app
