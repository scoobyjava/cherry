from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import Agent

class WebScrapingAgent(Agent):
    """Agent specialized in web scraping and data extraction."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.config = config or {}
        self.timeout = self.config.get('timeout', 30)
        self.user_agent = self.config.get('user_agent', 'CherryBot Web Scraper/1.0')
        self.headers = {
            'User-Agent': self.user_agent,
            **self.config.get('headers', {})
        }
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize resources needed for web scraping."""
        # Could initialize proxy management, rate limiters, etc.
        pass
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process web scraping requests."""
        if 'url' not in request:
            return {"status": "error", "message": "URL is required"}
        
        url = request['url']
        selectors = request.get('selectors')
        
        try:
            result = await self.scrape_page(url, selectors)
            return {
                "status": "success",
                "data": result,
                "url": url,
                "agent_id": self.agent_id
            }
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "url": url,
                "agent_id": self.agent_id
            }
    
    async def scrape_page(self, url: str, selectors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Scrape a web page and extract structured data.
        
        Args:
            url: The URL to scrape
            selectors: Optional dictionary mapping data keys to CSS selectors
        
        Returns:
            Dictionary containing the scraped data
        
        Raises:
            ValueError: If the URL is invalid
            ConnectionError: If connection failed
            TimeoutError: If the request times out
            Exception: For other errors during scraping
        """
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL: {url}")
        
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            raise ValueError(f"Invalid URL format: {url}")
            
        try:
            # Use a thread pool to run the blocking requests call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
            )
            
            # Check response status code
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            metadata = {
                'title': soup.title.string if soup.title else None,
                'url': url,
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type'),
                'encoding': response.encoding,
            }
            
            # Process content based on content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Initialize result dictionary
            result = {
                'metadata': metadata,
                'content': {}
            }
            
            # If it's HTML and we have selectors
            if 'text/html' in content_type and selectors:
                for key, selector in selectors.items():
                    elements = soup.select(selector)
                    result['content'][key] = [el.get_text(strip=True) for el in elements]
            
            # If no selectors provided, extract common elements
            elif 'text/html' in content_type:
                result['content'] = {
                    'title': soup.title.string if soup.title else None,
                    'headings': [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
                    'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p')],
                    'links': [{'text': a.get_text(strip=True), 'href': a.get('href')} 
                             for a in soup.find_all('a') if a.get('href')],
                    'images': [{'alt': img.get('alt', ''), 'src': img.get('src')} 
                              for img in soup.find_all('img') if img.get('src')]
                }
            
            # For JSON responses
            elif 'application/json' in content_type:
                try:
                    result['content'] = response.json()
                except json.JSONDecodeError:
                    result['content'] = {'raw': response.text}
            
            # For other content types
            else:
                result['content'] = {'raw': response.text[:1000]}  # First 1000 chars
                
            return result
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout} seconds")
        
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Failed to connect to {url}")
        
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP error occurred: {e}")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error during request to {url}: {e}")
        
        except Exception as e:
            raise Exception(f"Failed to parse page content: {e}")

    async def extract_specific_data(self, html_content: str, data_mapping: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract specific data using provided CSS selectors."""
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        
        for key, selector in data_mapping.items():
            elements = soup.select(selector)
            result[key] = [element.get_text(strip=True) for element in elements]
            
        return result
