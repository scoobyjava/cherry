
import os
import logging
from typing import Optional, Literal, Dict, Any

from bootstrap import initialize_cherry
from logger import setup_logger
from api_routes import register_flask_routes, register_fastapi_routes

ServerType = Literal["flask", "fastapi"]

def create_app(server_type: ServerType = "flask", config_path: Optional[str] = None):
    """
    Create and configure a web application instance with the specified framework.
    
    Args:
        server_type: Either "flask" or "fastapi"
        config_path: Path to configuration file
        
    Returns:
        Configured web application instance
    """
    # Initialize Cherry AI system first
    cherry = initialize_cherry(config_path)
    
    # Setup logger
    logger = setup_logger("cherry_api", log_level=cherry.config.log_level)
    logger.info(f"Creating {server_type} application...")
    
    if server_type == "flask":
        from flask import Flask
        app = Flask("cherry_ai")
        
        # Register routes
        register_flask_routes(app)
        
    elif server_type == "fastapi":
        from fastapi import FastAPI
        app = FastAPI(
            title="Cherry AI API",
            description="API for interacting with the Cherry AI system",
            version="1.0.0"
        )
        
        # Register routes
        register_fastapi_routes(app)
        
    else:
        raise ValueError(f"Unsupported server type: {server_type}")
    
    logger.info(f"{server_type.capitalize()} application created successfully")
    return app

def run_server(
    server_type: ServerType = "flask",
    host: str = "0.0.0.0", 
    port: int = 5000,
    config_path: Optional[str] = None,
    debug: bool = False
):
    """
    Run the Cherry AI API server.
    
    Args:
        server_type: Either "flask" or "fastapi"
        host: Host to bind the server to
        port: Port to bind the server to
        config_path: Path to configuration file
        debug: Whether to run in debug mode
    """
    app = create_app(server_type, config_path)
    
    if server_type == "flask":
        app.run(host=host, port=port, debug=debug)
    elif server_type == "fastapi":
        import uvicorn
        uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the Cherry AI API server")
    parser.add_argument("--server", choices=["flask", "fastapi"], default="flask",
                       help="Server framework to use")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind the server to")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    run_server(
        server_type=args.server,
        host=args.host,
        port=args.port,
        config_path=args.config,
        debug=args.debug
    )
