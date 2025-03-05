
from typing import Dict, Any, List, Optional, Callable
import logging

from bootstrap import get_cherry_system

logger = logging.getLogger("cherry_api")

# Common request handler functions that will be used by both Flask and FastAPI

def handle_status_request() -> Dict[str, Any]:
    """Handler for status endpoint"""
    cherry = get_cherry_system()
    return cherry.status()

def handle_query_request(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Handler for query endpoint"""
    cherry = get_cherry_system()
    try:
        result = cherry.orchestrator.process_query(query, context or {})
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {"status": "error", "message": str(e)}

def handle_reset_request() -> Dict[str, Any]:
    """Handler for reset endpoint"""
    cherry = get_cherry_system()
    try:
        cherry.stop()
        cherry.start()
        return {"status": "success", "message": "Cherry AI system restarted successfully"}
    except Exception as e:
        logger.error(f"Error resetting Cherry AI: {str(e)}")
        return {"status": "error", "message": str(e)}

# FastAPI specific route definitions
def register_fastapi_routes(app):
    """Register routes for FastAPI application"""
    from fastapi import FastAPI, HTTPException, Body, Depends
    from pydantic import BaseModel

    class QueryRequest(BaseModel):
        query: str
        context: Optional[Dict[str, Any]] = None

    @app.get("/status")
    def api_status():
        return handle_status_request()

    @app.post("/query")
    def api_query(request: QueryRequest):
        result = handle_query_request(request.query, request.context)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

    @app.post("/reset")
    def api_reset():
        result = handle_reset_request()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result

# Flask specific route definitions
def register_flask_routes(app):
    """Register routes for Flask application"""
    from flask import Flask, request, jsonify

    @app.route("/status", methods=["GET"])
    def api_status():
        return jsonify(handle_status_request())

    @app.route("/query", methods=["POST"])
    def api_query():
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"status": "error", "message": "Missing query parameter"}), 400
            
        result = handle_query_request(data["query"], data.get("context"))
        if result["status"] == "error":
            return jsonify(result), 500
        return jsonify(result)

    @app.route("/reset", methods=["POST"])
    def api_reset():
        result = handle_reset_request()
        if result["status"] == "error":
            return jsonify(result), 500
        return jsonify(result)
