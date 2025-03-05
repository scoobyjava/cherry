import json
from typing import List, Optional

def generate_embedding(content: str, model: str = "text-embedding-ada-002", config_path: str = "/workspaces/cherry/benchmarks/benchmark_config.json") -> Optional[List[float]]:
    """
    Generate an embedding vector for the given content using OpenAI's API.
    
    Args:
        content: The text content to embed
        model: The embedding model to use
        config_path: Path to the configuration file
        
    Returns:
        A list of floating point values representing the embedding or None if generation failed
    """
    try:
        import openai
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Configure OpenAI
        openai_config = config.get('openai', {})
        openai.api_key = openai_config.get('api_key')
        if 'organization_id' in openai_config:
            openai.organization = openai_config.get('organization_id')
        
        # Generate embedding
        response = openai.Embedding.create(
            input=content,
            model=model
        )
        
        # Extract the embedding from the response
        embedding = response['data'][0]['embedding']
        return embedding
        
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None
