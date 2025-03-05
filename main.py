import asyncio
import sqlite3
import os
import sys
import argparse
from typing import Optional, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task import Task
from task_scheduler import TaskScheduler
from agents.manager import AgentManager
from services.spotify_service import SpotifyService
from services.smart_home_service import SmartHomeService
from search import InternetSearch
from cherry.core.claude import Claude
from bootstrap import initialize_cherry
from server import run_server
from scheduler.memory_health_tasks import MemoryHealthScheduler

def task_a():
    print("Running Task A")

def task_b():
    print("Running Task B")

def task_c():
    print("Running Task C")

scheduler = TaskScheduler()
scheduler.add_task(Task("TaskA", task_a))
scheduler.add_task(Task("TaskB", task_b, dependencies=["TaskA"]))
scheduler.add_task(Task("TaskC", task_c, dependencies=["TaskB"]))

scheduler.run()

async def main_async_function():
    try:
        await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Task was cancelled")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

async def start_application():
    # Initialize memory health scheduler
    memory_scheduler = MemoryHealthScheduler()
    memory_scheduler.start()

    # ...existing code...

def initialize_database():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    
    with open('database_schema.sql', 'r') as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()

def main():
    """Main entry point for Cherry AI system."""
    parser = argparse.ArgumentParser(description="Cherry AI System")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--api", action="store_true", help="Start API server")
    parser.add_argument("--server", choices=["flask", "fastapi"], default="flask",
                       help="Server framework to use if --api is specified")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the API server to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind the API server to")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Initialize Cherry AI system
    cherry = initialize_cherry(args.config)
    
    # If API flag is set, start the API server
    if args.api:
        run_server(
            server_type=args.server,
            host=args.host,
            port=args.port,
            config_path=args.config,
            debug=args.debug
        )
    else:
        # Keep the application running and handle user input
        try:
            print("Cherry AI system initialized. Press Ctrl+C to exit.")
            while True:
                cmd = input("> ")
                if cmd.lower() == "exit":
                    break
                elif cmd.lower() == "status":
                    print(cherry.status())
                else:
                    result = cherry.orchestrator.process_query(cmd, {})
                    print(result)
        except KeyboardInterrupt:
            print("\nShutting down Cherry AI system...")
        finally:
            cherry.stop()

if __name__ == "__main__":
    initialize_database()
    main()