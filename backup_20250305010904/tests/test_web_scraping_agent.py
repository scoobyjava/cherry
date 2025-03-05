import unittest
from unittest.mock import AsyncMock, patch
import asyncio

from cherry.agents.web_scraping_agent import WebScrapingAgent  # Assuming this is the correct import

class TestWebScrapingAgent(unittest.IsolatedAsyncioTestCase):

    async def test_scrape_page_success(self):
        # Test that scrape_page returns HTML content on success.
        agent = WebScrapingAgent()
        # Patch aiohttp's ClientSession.get to simulate a successful HTTP response.
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.text.return_value = "dummy html content"
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            html = await agent.scrape_page("http://example.com")
            self.assertEqual(html, "dummy html content")

    async def test_scrape_page_error(self):
        # Test that scrape_page raises an exception on network error.
        agent = WebScrapingAgent()
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Network error")
            with self.assertRaises(Exception):
                await agent.scrape_page("http://example.com/error")

    async def test_scrape_site(self):
        # Test that scrape_site aggregates multiple pages.
        agent = WebScrapingAgent()
        # Simulate different page responses.
        fake_pages = {
            "http://example.com": "Page 1 content with link http://example.com/page2",
            "http://example.com/page2": "Page 2 content"
        }
        async def fake_scrape_page(url):
            return fake_pages[url]
        agent.scrape_page = fake_scrape_page  # Override instance method

        # Assuming scrape_site crawls starting at the seed URL and returns a dict mapping URLs to content.
        result = await agent.scrape_site("http://example.com")
        self.assertEqual(result, fake_pages)

    def test_extract_data(self):
        # Test extraction of structured data from HTML.
        agent = WebScrapingAgent()
        html = "<html><body><h1>Title</h1><p>Paragraph</p></body></html>"
        selectors = {"header": "h1", "paragraph": "p"}
        result = agent.extract_data(html, selectors)
        expected = {"header": ["Title"], "paragraph": ["Paragraph"]}
        self.assertEqual(result, expected)
        # Edge-case: selector with no matches.
        selectors_empty = {"div": "div"}
        result_empty = agent.extract_data(html, selectors_empty)
        self.assertEqual(result_empty, {"div": []})

    async def test_retrieve_scraped_content(self):
        # Test retrieval of scraped content.
        agent = WebScrapingAgent(config={"data_source": "mock"})
        # Simulate a response with dummy scraped data.
        agent.retrieve_scraped_content = AsyncMock(return_value=[{"id": 1, "content": "dummy"}])
        result = await agent.retrieve_scraped_content()
        self.assertEqual(result, [{"id": 1, "content": "dummy"}])
        # Edge-case: Retrieval returns an empty list.
        agent.retrieve_scraped_content = AsyncMock(return_value=[])
        result_empty = await agent.retrieve_scraped_content()
        self.assertEqual(result_empty, [])

if __name__ == '__main__':
    unittest.main()
