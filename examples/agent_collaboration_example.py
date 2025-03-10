"""
Example usage of the Cherry AI Agent Collaboration Framework.
"""

import sys
import os

# Add the src directory to the path so we can import our module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.collaboration import DeveloperAgent, ReviewerAgent

def main():
    """Demonstrate the agent collaboration framework."""
    print("Cherry AI Agent Collaboration Demo\n")
    
    # Create our agents
    developer = DeveloperAgent("CherryDev")
    reviewer = ReviewerAgent("CherryReviewer")
    
    # Link the developer to the reviewer
    developer.set_reviewer(reviewer)
    
    # Define a simple task
    task = "Write a function to add two numbers"
    
    print(f"Task: {task}\n")
    print("Starting collaboration...\n")
    
    # Start the collaboration
    final_solution = developer.collaborate(task)
    
    print("\nFinal Solution:")
    print("==============")
    print(final_solution)

if __name__ == "__main__":
    main()
