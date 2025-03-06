import { useState, useEffect } from "react";

/**
 * Custom hook for fetching data from APIs with loading, error, and retry functionality
 * @template T The expected data type to be returned
 * @param {string} url The API endpoint to fetch data from
 * @param {RequestInit} [options] Optional fetch configuration
 * @returns {Object} Object containing data, loading state, error state and retry function
 */
export function useFetchData<T>(url: string, options?: RequestInit) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState<number>(0);

  // Function to trigger a manual retry
  const retry = () => setRetryCount((count) => count + 1);

  useEffect(() => {
    // Create AbortController for cleanup
    const controller = new AbortController();
    const signal = controller.signal;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Implement exponential backoff for retry attempts
        if (retryCount > 0) {
          const delay = Math.min(1000 * 2 ** (retryCount - 1), 10000);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }

        const response = await fetch(url, {
          ...options,
          signal,
          headers: {
            "Content-Type": "application/json",
            ...options?.headers,
          },
        });

        if (!response.ok) {
          throw new Error(
            `API error: ${response.status} ${response.statusText}`
          );
        }

        const result = await response.json();
        setData(result as T);
      } catch (err) {
        // Don't set error state for aborted requests
        if ((err as Error).name !== "AbortError") {
          console.error("Fetch error:", err);
          setError(err as Error);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Cleanup function to abort fetch on unmount or url/options change
    return () => controller.abort();
  }, [url, retryCount, JSON.stringify(options)]); // Serialize options for dependency tracking

  return { data, loading, error, retry };
}
