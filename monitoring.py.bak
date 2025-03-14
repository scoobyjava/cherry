<<<<<<< Tabnine <<<<<<<
# monitoring.py
from phoenix.trace import Span, capture_span
from litellm import completion
import functools
import os
import time

# Configure Phoenix#-
# Configure Phoenix using environment variables (populated from GitHub secrets)#+
PHOENIX_API_KEY = os.environ.get("PHOENIX_API_KEY")
PHOENIX_ENDPOINT = os.environ.get(
    "PHOENIX_ENDPOINT", "https://phoenix.berri.ai")


def phoenix_trace(func):
    """
    Decorator to wrap LiteLLM calls with Phoenix tracing and monitoring
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract model information
        model = kwargs.get("model", "unknown_model")

        # Start span
        with Span(
            name=f"litellm.completion.{model}",
            kind="llm",
            attributes={
                "llm.model": model,
                "llm.provider": model.split("/")[0] if "/" in model else "unknown",
                "llm.request_tokens": kwargs.get("max_tokens", 0),
            }
        ) as span:
            start_time = time.time()

            try:
                # Execute the LLM call
                response = await func(*args, **kwargs)

                # Calculate duration and token usage
                duration_ms = (time.time() - start_time) * 1000

                # Extract token usage if available
                usage = getattr(response, "usage", None)
                if usage:
                    span.set_attribute("llm.completion_tokens",
                                       usage.completion_tokens)
                    span.set_attribute("llm.prompt_tokens",
                                       usage.prompt_tokens)
                    span.set_attribute("llm.total_tokens", usage.total_tokens)

                span.set_attribute("llm.duration_ms", duration_ms)
                span.set_status("ok")

                return response

            except Exception as e:
                # Record error information
                span.set_status("error")
                span.record_exception(e)
                raise

    return wrapper

# Wrap LiteLLM completion function#-

#-
@phoenix_trace
async def monitored_completion(*args, **kwargs):
    """
    Wrapped version of litellm.completion with Phoenix monitoring
    """
    return await completion(*args, **kwargs)
>>>>>>> Tabnine >>>>>>># {"source":"chat"}
