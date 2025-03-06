import asyncio
import logging
from typing import Dict, List, Optional, TypeVar, Generic, Union, Any
import aiohttp
from aiohttp import ClientResponseError, ClientConnectorError, ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class DataFetchResult(Generic[T]):
    """
    Container class for API fetch results with strong typing support.

    Attributes:
        data: The successfully fetched data
        error: Error message if request failed
        status_code: HTTP status code received from the server
    """

    def __init__(
        self,
        data: Optional[T] = None,
        error: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        self.data = data
        self.error = error
        self.status_code = status_code

    @property
    def success(self) -> bool:
        """Indicates if the request was successful."""
        return self.error is None and self.status_code and 200 <= self.status_code < 300


def compute_backoff_delay(retry: int, retry_after: int = 0) -> float:
    """
    Compute exponential backoff delay.
    If 'retry_after' header is provided, use it; otherwise exponentiate.
    """
    return retry_after if retry_after > 0 else float(2 ** retry)


class ApiClient:
    """
    Client for making API requests with built-in retry and error handling.

    Features:
    - Automatic retries with exponential backoff
    - Timeout handling
    - Comprehensive error reporting
    - Type annotations for better IDE support
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for all API requests
            headers: Default headers for requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch_data(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_codes: List[int] = [429, 500, 502, 503, 504]
    ) -> DataFetchResult[T]:
        """
        Fetch data from the API with automatic retries.

        Args:
            endpoint: API endpoint to call (without base URL)
            method: HTTP method to use
            params: Query parameters
            json_data: JSON data to send in request body
            retry_codes: HTTP status codes that should trigger a retry

        Returns:
            DataFetchResult object containing the response data or error info
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        current_try = 0

        while current_try <= self.max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        params=params,
                        json=json_data,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        status_code = response.status

                        if 200 <= status_code < 300:
                            data = await response.json()
                            return DataFetchResult(data=data, status_code=status_code)

                        # Check if we should retry based on status code
                        if status_code in retry_codes and current_try < self.max_retries:
                            retry_after = int(
                                response.headers.get('Retry-After', 0))
                            backoff_time = compute_backoff_delay(
                                current_try, retry_after)
                            logger.warning(
                                f"Request failed with status {status_code}. Retrying in {backoff_time:.1f}s...")
                            await asyncio.sleep(backoff_time)
                            current_try += 1
                            continue

                        error_text = await response.text()
                        return DataFetchResult(
                            error=f"HTTP {status_code}: {error_text}",
                            status_code=status_code
                        )

            except ClientResponseError as e:
                logger.error(f"Response error: {str(e)}")
                return DataFetchResult(error=f"Response error: {str(e)}")

            except ClientConnectorError as e:
                logger.error(f"Connection error: {str(e)}")

                if current_try < self.max_retries:
                    backoff_time = compute_backoff_delay(current_try)
                    logger.warning(
                        f"Connection failed. Retrying in {backoff_time:.1f}s...")
                    await asyncio.sleep(backoff_time)
                    current_try += 1
                    continue

                return DataFetchResult(error=f"Connection error: {str(e)}")

            except asyncio.TimeoutError:
                logger.error("Request timed out")

                if current_try < self.max_retries:
                    backoff_time = compute_backoff_delay(current_try)
                    logger.warning(
                        f"Request timed out. Retrying in {backoff_time:.1f}s...")
                    await asyncio.sleep(backoff_time)
                    current_try += 1
                    continue

                return DataFetchResult(error="Request timed out")

            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return DataFetchResult(error=f"Unexpected error: {str(e)}")


# Example usage
async def main() -> None:
    """Example function demonstrating API client usage."""
    api_client = ApiClient(base_url="http://localhost:8000")

    # Fetch a list of items
    result = await api_client.fetch_data("api/items")

    if result.success:
        items = result.data
        logger.info(f"Successfully retrieved {len(items)} items")
        for item in items:
            logger.info(f"Item: {item['name']} - {item['status']}")
    else:
        logger.error(f"Failed to fetch data: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
