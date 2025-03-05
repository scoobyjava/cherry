from typing import Dict, Any, List, Optional
import asyncio
from bs4 import BeautifulSoup
import asyncpg  # added import for PostgreSQL connection

from .base import Agent

class CodeGeneratorAgent(Agent):
    """Agent specialized in generating code based on specifications."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.supported_languages = config.get('languages', ['python', 'javascript']) if config else ['python', 'javascript']
        self.model = config.get('model', 'default') if config else 'default'
    
    async def initialize(self) -> None:
        """Initialize any resources needed for code generation."""
        # Load any necessary models or resources
        pass
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process code generation requests."""
        if 'specification' not in request:
            return {"status": "error", "message": "Specification is required"}
        
        specification = request['specification']
        language = request.get('language', 'python')
        
        if language not in self.supported_languages:
            return {"status": "error", "message": f"Language {language} not supported"}
        
        code = await self.generate_code(specification, language)
        tests = await self.generate_tests(code, language) if request.get('generate_tests', False) else None
        
        return {
            "status": "success",
            "code": code,
            "tests": tests,
            "language": language,
            "agent_id": self.agent_id
        }
    
    async def generate_code(self, specification: str, language: str) -> str:
        """Generate code based on the specification and language."""
        # Implementation of code generation logic
        # This is a placeholder
        await asyncio.sleep(1.5)  # Simulate generation time
        return f"# Generated {language} code\ndef example_function():\n    print('Hello, World!')"
    
    async def generate_tests(self, code: str, language: str) -> str:
        """Generate tests for the provided code."""
        # Implementation of test generation logic
        # This is a placeholder
        await asyncio.sleep(0.8)  # Simulate test generation time
        return f"# Generated tests\ndef test_example_function():\n    assert True"
    
    async def fallback_retrieve_data(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve scraped data directly from PostgreSQL using pgvector-based semantic similarity.
        Expects 'postgres_dsn' in config for database connection.
        """
        postgres_dsn = self.config.get('postgres_dsn', 'postgresql://user:pass@localhost/db')
        conn = await asyncpg.connect(postgres_dsn)
        try:
            query = """
            SELECT id, content, embedding
            FROM scraped_data
            WHERE embedding IS NOT NULL
            ORDER BY embedding <-> $1
            LIMIT $2;
            """
            rows = await conn.fetch(query, query_vector, limit)
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    def extract_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, List[Any]]:
        """Extract structured data from HTML using provided selectors."""
        soup = BeautifulSoup(html, "lxml")
        data = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            data[key] = [el.get_text(strip=True) for el in elements]
        return data
