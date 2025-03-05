import asyncio
import aiohttp
import urllib.robotparser
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

async def check_robots(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(robots_url) as response:
                if response.status != 200:
                    return True  # Assume allowed if no robots.txt
                content = await response.text()
    except Exception:
        return True  # On error, allow by default
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(content.splitlines())
    return rp.can_fetch(user_agent, url)

async def scrape_site(url: str, depth: int = 0, max_depth: int = 2, visited=None) -> dict:
    if visited is None:
        visited = set()
    if url in visited:
        return {}
    visited.add(url)

    allowed = await check_robots(url)
    if not allowed:
        return {"url": url, "error": "Disallowed by robots.txt", "links": []}

    await asyncio.sleep(1)  # Throttle requests

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()
    except Exception as e:
        return {"url": url, "error": str(e), "links": []}

    soup = BeautifulSoup(content, "html.parser")
    anchors = soup.find_all("a")
    links = []
    for a in anchors:
        href = a.get("href")
        if href:
            link = urljoin(url, href)
            if urlparse(link).netloc == urlparse(url).netloc:
                links.append(link)

    child_results = []
    if depth < max_depth:
        tasks = []
        for link in links:
            if link not in visited:
                tasks.append(scrape_site(link, depth + 1, max_depth, visited))
        if tasks:
            results = await asyncio.gather(*tasks)
            child_results.extend([res for res in results if res])
    
    return {
        "url": url,
        "content": content,
        "links": child_results
    }
