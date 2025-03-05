import asyncio
import sys
import os

# Add the root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import AgentManager

async def run_agents():
    """Demonstration of how to use different types of agents."""
    manager = AgentManager()
    
    print("Initializing agents...")
    researcher = await manager.initialize_agent(
        "researcher", 
        "research-agent", 
        {"sources": ["web", "academic", "news"]}
    )
    
    code_generator = await manager.initialize_agent(
        "code_generator", 
        "code-agent",
        {"languages": ["python", "javascript", "go"]}
    )
    
    creative = await manager.initialize_agent(
        "creative",
        "creative-agent",
        {"styles": ["narrative", "poetic", "technical", "casual"]}
    )
    
    # Process research request
    print("\nProcessing research request...")
    research_result = await manager.process_request(
        "research-agent", 
        {"query": "advances in quantum computing"}
    )
    print(f"Research result: {research_result}")
    
    # Process code generation request
    print("\nProcessing code generation request...")
    code_result = await manager.process_request(
        "code-agent",
        {
            "specification": "Create a function that calculates Fibonacci numbers",
            "language": "python",
            "generate_tests": True
        }
    )
    print(f"Generated code: {code_result.get('code', 'No code generated')}")
    if code_result.get('tests'):
        print(f"Generated tests: {code_result.get('tests')}")
    
    # Process creative content request
    print("\nProcessing creative content request...")
    creative_result = await manager.process_request(
        "creative-agent",
        {
            "prompt": "Write a short story about AI helping humanity",
            "style": "narrative"
        }
    )
    print(f"Creative content: {creative_result.get('content', 'No content generated')}")
    
    # Clean up
    print("\nCleaning up agents...")
    await manager.cleanup()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(run_agents())
