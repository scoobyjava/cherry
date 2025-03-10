"""
Knowledge search module for Cherry.

This module provides functionality to search for relevant information
in the Cherry codebase and documentation using Sourcegraph Cody's API.
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Simple in-memory cache for queries
_query_cache = {}
_cache_expiry = {}  # Store expiration times
CACHE_DURATION = timedelta(minutes=30)  # Cache results for 30 minutes
RATE_LIMIT_DELAY = 1.0  # Seconds to wait between API calls

# Last API call timestamp for rate limiting
_last_api_call = 0


def search_knowledge(query: str) -> str:
    """
    Search for relevant information related to a query using Sourcegraph Cody API.

    Args:
        query: A natural language query string (e.g., 'how to validate user input in Cherry's codebase')

    Returns:
        A concise summary of the top relevant results, or an error message if the search fails.

    Example:
        >>> result = search_knowledge("how to handle authentication in Cherry")
        >>> print(result)
        "Cherry's authentication is handled primarily in auth.py using JWT tokens..."
    """
    # Check cache first
    cached_result = _get_cached_result(query)
    if cached_result is not None:
        return cached_result

    try:
        # Call Sourcegraph API
        search_results = _call_sourcegraph_api(query)

        # Process and summarize results
        if not search_results:
            return "No results found for your query."

        summary = _summarize_results(search_results, query)

        # Cache the result
        _cache_result(query, summary)

        return summary

    except Exception as e:
        # Log the error but return gracefully
        print(f"Error in search_knowledge: {str(e)}")
        return f"Unable to retrieve information. The search service may be unavailable."


def _call_sourcegraph_api(query: str) -> List[Dict[str, Any]]:
    """
    Make a call to the Sourcegraph Cody API.

    Args:
        query: The search query string

    Returns:
        A list of search result items

    Raises:
        Exception: If the API call fails
    """
    global _last_api_call

    # Respect rate limits
    current_time = time.time()
    if current_time - _last_api_call < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - (current_time - _last_api_call))

    # Update the last call time
    _last_api_call = time.time()

    # TODO: Replace with actual Sourcegraph Cody API implementation
    # This is currently a placeholder

    # For now, we'll simulate an API response
    # In a real implementation, this would be:
    # headers = {"Authorization": "Bearer YOUR_API_KEY"}
    # response = requests.get(
    #     "https://sourcegraph.com/api/search",
    #     params={"q": query},
    #     headers=headers,
    #     timeout=10
    # )
    # return response.json().get("results", [])

    # Placeholder implementation
    if "authentication" in query.lower():
        return [
            {"path": "auth.py",
                "content": "def authenticate_user(username, password):\n    # Validate credentials\n    # Generate JWT token\n    return token"},
            {"path": "middleware.py",
                "content": "def auth_middleware(request):\n    # Verify JWT token\n    # Return user or 401"}
        ]
    elif "validation" in query.lower() or "user input" in query.lower():
        return [
            {"path": "validators.py",
                "content": "def validate_input(data, schema):\n    # Validate against schema\n    if not valid:\n        raise ValidationError()"},
            {"path": "forms.py",
                "content": "class UserForm:\n    def validate(self):\n        # Check required fields\n        # Sanitize inputs"}
        ]
    else:
        # Default empty response
        return []


def _summarize_results(results: List[Dict[str, Any]], query: str) -> str:
    """
    Summarize the search results into a concise, readable format.

    Args:
        results: List of search result items from the API
        query: The original search query

    Returns:
        A formatted summary string
    """
    if not results:
        return "No results found for your query."

    summary_parts = ["Here are the most relevant results:"]

    for i, result in enumerate(results[:5]):  # Limit to top 5 results
        path = result.get("path", "unknown")
        content = result.get("content", "").strip()

        # Create a summary for this result
        content_summary = content[:150] + \
            "..." if len(content) > 150 else content
        summary_parts.append(
            f"\n{i+1}. In {path}:\n```\n{content_summary}\n```")

    # Add a concluding note
    summary_parts.append(
        "\nThese code snippets show the relevant implementations for your query.")

    return "\n".join(summary_parts)


def _get_cached_result(query: str) -> Optional[str]:
    """
    Check if a query result is available in cache and not expired.

    Args:
        query: The search query string

    Returns:
        The cached result if available, None otherwise
    """
    normalized_query = query.lower().strip()

    if normalized_query in _query_cache:
        # Check if the cache has expired
        if datetime.now() < _cache_expiry.get(normalized_query, datetime.min):
            return _query_cache[normalized_query]
        else:
            # Cache expired, remove it
            del _query_cache[normalized_query]
            if normalized_query in _cache_expiry:
                del _cache_expiry[normalized_query]

    return None


def _cache_result(query: str, result: str) -> None:
    """
    Cache a query result for future use.

    Args:
        query: The search query string
        result: The result to cache
    """
    normalized_query = query.lower().strip()
    _query_cache[normalized_query] = result
    _cache_expiry[normalized_query] = datetime.now() + CACHE_DURATION
