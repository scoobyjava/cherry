from typing import Dict, Any, List, Optional, Union
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import requests

from .base import Agent

class WebScrapingAgent(Agent):
    """Agent specialized in comprehensive and efficient web scraping tasks."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.config = config or {}
        
        # Default configuration with sensible values
        self.headers = self.config.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 2)
        self.respect_robots = self.config.get('respect_robots', True)
        
        # Session will be initialized in initialize()
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.timeout = 5  # seconds
    
    async def initialize(self) -> None:
        """Initialize resources needed for web scraping."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        self.logger.info(f"WebScrapingAgent '{self.agent_id}' initialized")
    
    async def cleanup(self) -> None:
        """Clean up resources when agent is no longer needed."""
        if self.session:
            await self.session.close()
            self.session = None
        self.logger.info(f"WebScrapingAgent '{self.agent_id}' cleaned up")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        url = request.get("url")
        if not url:
            return {"status": "error", "message": "URL required"}
        selectors = request.get("selectors", {})
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, requests.get, url)
        if response.status_code != 200:
            return {"status": "error", "message": "Unable to fetch URL"}
        html = response.text
        soup = BeautifulSoup(html, "lxml")
        data = { key: [el.get_text(strip=True) for el in soup.select(selector)]
                 for key, selector in selectors.items() }
        return {"status": "success", "data": data}
    
    async def fetch_url(self, url: str, method: str = 'GET', params: Dict = None, 
                        data: Dict = None) -> Optional[str]:
        """Fetch content from a URL with retry logic."""
        if not self.session:
            await self.initialize()
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method=method, 
                    url=url, 
                    params=params,
                    json=data if method == 'POST' else None,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self.logger.warning(f"Request failed with status {response.status} for URL: {url}")
                        if 400 <= response.status < 500:
                            # Don't retry client errors
                            return None
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                self.logger.warning(f"Attempt {attempt+1} failed for URL {url}: {str(e)}")
            
            # Wait before retrying
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        return None
    
    async def extract_data(self, content: str, extraction_rules: Dict[str, Any], 
                           parse_type: str = 'html') -> Union[Dict[str, Any], List[Any], str]:
        """Extract data from content based on extraction rules."""
        if parse_type == 'html':
            return await self.extract_from_html(content, extraction_rules)
        elif parse_type == 'json':
            return await self.extract_from_json(content, extraction_rules)
        else:
            return content  # Return raw text
    
    async def extract_from_html(self, html_content: str, 
                                extraction_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from HTML content using BeautifulSoup and extraction rules."""
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        
        for key, rule in extraction_rules.items():
            if isinstance(rule, dict):
                selector = rule.get('selector', '')
                attribute = rule.get('attribute', None)
                multiple = rule.get('multiple', False)
                
                if multiple:
                    elements = soup.select(selector)
                    if attribute:
                        result[key] = [el.get(attribute) for el in elements if el.has_attr(attribute)]
                    else:
                        result[key] = [el.get_text(strip=True) for el in elements]
                else:
                    element = soup.select_one(selector)
                    if element:
                        if attribute:
                            if element.has_attr(attribute):
                                result[key] = element.get(attribute)
                            else:
                                result[key] = None
                        else:
                            result[key] = element.get_text(strip=True)
                    else:
                        result[key] = None
            else:
                # Simple string selector
                element = soup.select_one(rule)
                result[key] = element.get_text(strip=True) if element else None
                
        return result
    
    async def extract_from_json(self, json_content: str, 
                                extraction_paths: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from JSON content using path rules."""
        import json
        from jsonpath_ng import parse
        
        try:
            json_data = json.loads(json_content)
            result = {}
            
            for key, path in extraction_paths.items():
                jsonpath_expr = parse(path)
                matches = jsonpath_expr.find(json_data)
                if matches:
                    # If multiple matches, return as list, otherwise return single value
                    values = [match.value for match in matches]
                    result[key] = values if len(values) > 1 else values[0]
                else:
                    result[key] = None
                    
            return result
        except json.JSONDecodeError:
            self.logger.error("Failed to parse JSON content")
            return {}
    
    async def crawl_website(self, start_url: str, max_depth: int = 2, 
                            max_pages: int = 20) -> Dict[str, Any]:
        """Crawl a website starting from a URL, up to specified depth and page limits."""
        visited_urls = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        results = {}
        count = 0
        
        domain = urlparse(start_url).netloc
        
        while to_visit and count < max_pages:
            url, depth = to_visit.pop(0)
            
            if url in visited_urls:
                continue
                
            if urlparse(url).netloc != domain:
                continue  # Stay on the same domain
                
            visited_urls.add(url)
            count += 1
            
            content = await self.fetch_url(url)
            if not content:
                continue
                
            # Store the content
            results[url] = content
            
            # Don't extract further links if we've reached max depth
            if depth >= max_depth:
                continue
                
            # Extract links for next level
            soup = BeautifulSoup(content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                if href.startswith('/'):
                    # Convert relative URL to absolute
                    next_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}{href}"
                elif href.startswith(('http://', 'https://')):
                    next_url = href
                else:
                    continue
                    
                if next_url not in visited_urls:
                    to_visit.append((next_url, depth + 1))
                    
        return {
            "pages_crawled": count,
            "results": results
        }

    def scrape_page(self, url: str) -> Dict[str, Any]:
        """Recursively scrape a page, validate response, and parse HTML into structured JSON."""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()  # raises an HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
        
        # Validate response content-type is HTML
        if 'text/html' not in response.headers.get('Content-Type', ''):
            return {"status": "error", "message": "Invalid content type"}
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title from the page
        title = soup.title.string if soup.title else ""
        # Extract all links from <a> tags
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        # Extract text content
        content = soup.get_text(separator=' ', strip=True)

        return {
            "status": "success",
            "url": url,
            "title": title,
            "links": links,
            "content": content
        }

    async def store_scraped_data(self, content: str, metadata: dict) -> int:
        """
        Store scraped content into PostgreSQL and insert its embedding into Pinecone.
        Returns the PostgreSQL record ID.
        """
        try:
            embedding = await self.generate_embedding(content)
        except Exception as e:
            # Handle embedding generation error
            raise Exception(f"Embedding generation failed: {e}")
        
        try:
            # Begin PostgreSQL transaction
            with self.db_conn:
                with self.db_conn.cursor() as cur:
                    # Insert scraped data
                    # Assume 'scraped_data' table has columns: id (serial), content, metadata (json)
                    insert_query = """
                        INSERT INTO scraped_data (content, metadata)
                        VALUES (%s, %s)
                        RETURNING id;
                    """
                    cur.execute(insert_query, (content, metadata))
                    record = cur.fetchone()
                    record_id = record[0]
            
            # Insert embedding into Pinecone using record_id as identifier
            try:
                self.pinecone_client.upsert(items=[{"id": record_id, "values": embedding}])
            except Exception as pinecone_err:
                # Log Pinecone error; decide if additional compensation is needed
                raise Exception(f"Pinecone upsert failed for record {record_id}: {pinecone_err}")

            return record_id
        except Exception as db_err:
            # In case of any DB error, rollback is automatically handled by the context manager
            raise Exception(f"Database error during store_scraped_data: {db_err}")

    def retrieve_scraped_content(self, query: str, top_n: int = 5) -> list:
        # Embed query text using OpenAI embedding
        # e.g., embedding_response = openai.Embedding.create(input=query, model="text-embedding-ada-002")
        # query_embedding = embedding_response['data'][0]['embedding']
        
        # Query Pinecone for most relevant memories
        # e.g., results = pinecone_index.query(vector=query_embedding, top_k=top_n)
        
        # Fetch matching records from PostgreSQL as structured JSON
        # e.g., connect to PostgreSQL, execute a SELECT based on result IDs from Pinecone,
        # convert rows to JSON/dictionary format
        
        # Return the list of structured JSON records
        return []  # Placeholder for actual implementation

    def fetch_data(self, url: str) -> str:
        # Validate URL for HTTPS only to prevent insecure requests
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != 'https':
            raise ValueError("Only HTTPS URLs are allowed for secure requests")
        
        headers = {"User-Agent": "Cherry/1.0 (compatible; SecureScraper)"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch data from {url}: {e}")
            raise
        return response.text
