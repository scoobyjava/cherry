from typing import Dict, Any, List, Optional, Union
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse

from .base import Agent

class WebScrapingAgent(Agent):
    """Agent specialized in web scraping operations."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.headers = config.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }) if config else {}
        self.timeout = config.get('timeout', 30) if config else 30
        self.session = None
        
    async def initialize(self) -> None:
        """Initialize resources needed for web scraping."""
        self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.session:
            await self.session.close()
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process scraping requests."""
        if 'url' not in request:
            return {"status": "error", "message": "URL is required"}
        
        url = request['url']
        
        if request.get('type') == 'site':
            depth = request.get('depth', 1)
            result = await self.scrape_site(url, depth)
            return {
                "status": "success", 
                "data": result,
                "type": "site_scrape",
                "url": url,
                "depth": depth,
                "agent_id": self.agent_id
            }
        else:
            selectors = request.get('selectors', {})
            result = await self.scrape_page(url)
            if selectors and result.get('html_content'):
                extracted = await self.extract_data(result['html_content'], selectors)
                result['extracted_data'] = extracted
            
            return {
                "status": "success",
                "data": result,
                "type": "page_scrape",
                "url": url,
                "agent_id": self.agent_id
            }
    
    async def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        Scrapes and returns structured content from a single web page.
        
        Args:
            url: The URL of the page to scrape
            
        Returns:
            A dictionary containing:
                - status: Success or error status
                - html_content: The raw HTML content if successful
                - text_content: The extracted text content
                - title: The page title if available
                - metadata: Any metadata extracted from the page
        """
        if not self.session:
            await self.initialize()
        
        try:
            async with self.session.get(url, timeout=self.timeout) as response:
                if response.status != 200:
                    return {
                        "status": "error",
                        "message": f"HTTP error {response.status}",
                        "url": url
                    }
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract basic information
                title = soup.title.string if soup.title else None
                
                # Extract metadata
                metadata = {}
                for meta in soup.find_all('meta'):
                    name = meta.get('name') or meta.get('property')
                    if name and meta.get('content'):
                        metadata[name] = meta.get('content')
                
                return {
                    "status": "success",
                    "url": url,
                    "html_content": html_content,
                    "text_content": soup.get_text(separator=' ', strip=True),
                    "title": title,
                    "metadata": metadata
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "url": url
            }
    
    async def scrape_site(self, url: str, depth: int = 1) -> List[Dict[str, Any]]:
        """
        Performs recursive scraping of multiple pages within a site, based on specified depth.
        
        Args:
            url: The base URL to start scraping from
            depth: How many levels of links to follow (default=1)
            
        Returns:
            A list of dictionaries with scraped information from each page
        """
        if depth < 1:
            return []
        
        visited_urls = set()
        results = []
        base_domain = urllib.parse.urlparse(url).netloc
        
        async def _scrape_recursive(current_url, current_depth):
            if current_depth > depth or current_url in visited_urls:
                return
            
            visited_urls.add(current_url)
            page_result = await self.scrape_page(current_url)
            results.append(page_result)
            
            # Don't follow links on error or if we've reached max depth
            if page_result.get("status") != "success" or current_depth == depth:
                return
            
            # Extract links for next level
            soup = BeautifulSoup(page_result.get("html_content", ""), 'html.parser')
            tasks = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urllib.parse.urljoin(current_url, href)
                
                # Only follow links within the same domain
                if urllib.parse.urlparse(full_url).netloc == base_domain and full_url not in visited_urls:
                    tasks.append(_scrape_recursive(full_url, current_depth + 1))
            
            await asyncio.gather(*tasks)
        
        await _scrape_recursive(url, 1)
        return results
    
    async def extract_data(self, html_content: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extracts structured data from HTML content using provided CSS selectors or XPath.
        
        Args:
            html_content: The HTML content to parse
            selectors: A dictionary mapping data keys to CSS selectors or XPath expressions
                       Format: {'data_key': 'selector'}
                       
        Returns:
            A dictionary with extracted data matching the selector keys
        """
        if not html_content:
            return {}
            
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        
        for key, selector in selectors.items():
            # Determine if selector is XPath (starts with /) or CSS selector
            is_xpath = selector.startswith('/')
            
            if is_xpath:
                # For XPath we would need lxml
                # This is a placeholder - in a real implementation you'd use lxml's xpath
                result[key] = "[XPath not implemented in this example]"
            else:
                # CSS selector
                elements = soup.select(selector)
                if elements:
                    # If multiple elements, collect as list
                    if len(elements) > 1:
                        result[key] = [elem.get_text(strip=True) for elem in elements]
                    else:
                        result[key] = elements[0].get_text(strip=True)
                else:
                    result[key] = None
                    
        return result
