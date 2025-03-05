from typing import Dict, Any, List
import asyncio
from bs4 import BeautifulSoup
from .base import Agent
from cherry.utils.connection_helpers import get_postgresql_connection, get_pinecone_index  # changed code

class WebScrapingAgent(Agent):
    """Agent specialized in web scraping and sharing data through Cherry's shared memory system."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        # Initialize shared memory connections (PostgreSQL & Pinecone)
        self.db_conn = get_postgresql_connection(config.get("postgres"))  # changed code
        self.pinecone_index = get_pinecone_index(config.get("pinecone"))  # changed code
    
    async def scrape_data(self, url: str, selectors: Dict[str, str]) -> Dict[str, List[str]]:
        # Placeholder: Perform actual HTTP request and parsing.
        # For demonstration, using a dummy HTML string.
        html = "<html><!-- ...existing HTML... --></html>"
        soup = BeautifulSoup(html, "lxml")
        data = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            data[key] = [el.get_text(strip=True) for el in elements]
        return data
    
    async def share_scraped_data(self, data: Dict[str, List[str]], namespace: str) -> None:
        """
        Share scraped data with other agents using Cherry's shared memory system (PostgreSQL & Pinecone).
        Tags the data with the provided namespace.
        """
        # Share to PostgreSQL
        await self.share_to_postgresql(data, namespace)
        # Share to Pinecone
        await self.share_to_pinecone(data, namespace)
    
    async def share_to_postgresql(self, data: Dict[str, List[str]], namespace: str):
        # Placeholder: Implement logic to write data to PostgreSQL with the namespace.
        await asyncio.sleep(0.5)  # Simulate database write delay.
        print(f"Data shared to PostgreSQL under namespace: {namespace}")
    
    async def share_to_pinecone(self, data: Dict[str, List[str]], namespace: str):
        # Placeholder: Implement upsert logic to Pinecone with the provided namespace as metadata.
        await asyncio.sleep(0.5)  # Simulate Pinecone operation delay.
        print(f"Data shared to Pinecone under namespace: {namespace}")
