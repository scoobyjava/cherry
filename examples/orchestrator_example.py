import logging
import sys
import os

# Add the parent directory to the path to import the cherry modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cherry.core.orchestrator import Orchestrator
from agents.researcher import ResearcherAgent
from agents.developer import DeveloperAgent
from agents.writer import WriterAgent

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # Create an orchestrator
    orchestrator = Orchestrator(default_agent_type="researcher")
    
    # Register specialized agents
    orchestrator.register_agent("researcher", ResearcherAgent(), 
                               ["research", "information retrieval", "data analysis"])
    orchestrator.register_agent("developer", DeveloperAgent())
    orchestrator.register_agent("writer", WriterAgent())
    
    # List registered agents
    print(f"Registered agents: {orchestrator.list_agents()}")
    
    # Example tasks for different agents
    tasks = [
        "Research the history of artificial intelligence",
        "Write a blog post about climate change",
        "Debug my Python code that has a recursion error",
        "Find information about quantum computing advances",
        "Generate a creative story about space exploration"
    ]
    
    # Process each task with the appropriate agent
    for task in tasks:
        print(f"\nProcessing task: {task}")
        try:
            result = orchestrator.route_task(task)
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
