import asyncio
import json
from config import load_config
from memory_chroma import ChromaMemory
from agents.creative import CreativeAgent

async def demonstrate_creative_agent():
    """Demonstrate the capabilities of the creative agent."""
    config = load_config()
    memory = ChromaMemory(config)
    
    # Initialize the creative agent
    creative_agent = CreativeAgent(config, memory)
    
    # Example 1: Generate a short story
    print("Example 1: Generate a short story")
    print("-" * 50)
    story_result = await creative_agent.generate_writing(
        prompt="A time traveler accidentally changes history by stepping on a butterfly",
        format="short story",
        style="detailed"
    )
    print(story_result["content"])
    print("\n" + "=" * 80 + "\n")
    
    # Example 2: Generate business ideas
    print("Example 2: Generate business ideas")
    print("-" * 50)
    ideas_result = await creative_agent.generate_ideas(
        prompt="Sustainable products for reducing plastic waste in households",
        count=3,
        domain="business",
        style="practical"
    )
    print(ideas_result["content"])
    print("\n" + "=" * 80 + "\n")
    
    # Example 3: Generate design concept
    print("Example 3: Generate design concept")
    print("-" * 50)
    design_result = await creative_agent.generate_design(
        prompt="A smartphone app that helps people connect with local community events",
        medium="mobile app",
        constraints=["Must be accessible to users with disabilities", 
                     "Should work offline when needed"]
    )
    print(design_result["content"])
    print("\n" + "=" * 80 + "\n")
    
    # Example 4: Refine content
    print("Example 4: Refine content")
    print("-" * 50)
    original_content = story_result["content"]
    refine_result = await creative_agent.refine_content(
        content=original_content,
        feedback="Make the story more suspenseful and add a twist ending"
    )
    print(refine_result["refined_content"])
    
if __name__ == "__main__":
    asyncio.run(demonstrate_creative_agent())
