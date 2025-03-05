from cherry.feedback.system_evaluator import get_evaluator
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from prefect import task, Flow
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


async def run_periodic_evaluation():
    """Run system evaluation every 24 hours and save the report"""
    while True:
        evaluator = get_evaluator()
        report = await evaluator.generate_report()

        # Save report to file
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   "reports", f"system_evaluation_{timestamp}.md")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w") as f:
            f.write(report)

        logger.info(f"System evaluation report generated: {report_path}")

        # Wait 24 hours
        await asyncio.sleep(86400)


class ResourceOptimizationAgent(Agent):
    """Monitors and optimizes system resource usage across agents."""

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # Analyze memory usage patterns
        # Suggest code optimizations
        # Implement caching strategies for repeated operations


class APIIntegrationAgent(Agent):
    """Manages connections to external APIs, handling authentication, 
    rate limiting and request optimization."""

    def __init__(self):
        super().__init__("api_integration_agent", "Manages external API connections")
        self.api_performance_metrics = {}
        self.rate_limit_tracker = {}


class KnowledgeRetrievalAgent(Agent):
    """Specialized for efficient vector search and retrieval operations."""

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        query_type = task_data.get("query_type", "semantic")
        if query_type == "semantic":
            return await self._vector_search(task_data["query"])
        elif query_type == "factual":
            return await self._structured_search(task_data["query"])


# Update to PlanningAgent's collaborate_on_task method
async def collaborate_on_task(self, task: dict, dependencies: dict = None) -> dict:
    """Enhanced collaboration with selective data sharing."""
    # Check for circular dependencies
    if dependencies:
        self._verify_dependency_graph(dependencies)

    # Create task-specific context with minimal necessary data
    task_context = self._extract_relevant_context(task)

    # Add compression for large payloads
    compressed_payload = self._compress_if_needed(task_context)

    message = {
        "sender": self.name,
        "task_id": task.get("id", str(uuid.uuid4())),
        "context_level": task.get("context_importance", "medium"),
        "payload": compressed_payload,
        "expected_response_format": task.get("response_format")
    }

    return await message_bus(message)


# Update to multi_layer_fallback in PlanningAgent
async def multi_layer_fallback(self, api_call, prompt: str, *args, **kwargs):
    """Enhanced fallback with learning capabilities."""
    # Create a cache key based on the function signature and args
    cache_key = self._generate_cache_key(api_call.__name__, args, kwargs)

    # Check if we have a cached successful response
    if self.successful_calls_cache.get(cache_key):
        return self.successful_calls_cache[cache_key]

    # Try the optimal path first
    try:
        result = await api_call(prompt, *args, **kwargs)
        # Cache successful calls for similar future requests
        self.successful_calls_cache[cache_key] = result
        return result
    except Exception as e:
        # Log error pattern for future prevention
        self._log_error_pattern(e, api_call.__name__, prompt)

        # Try fallbacks with progressively simplified requests
        return await self._execute_fallback_chain(prompt, e, *args, **kwargs)


def initialize_monitoring():
    """Setup OpenTelemetry for distributed tracing and metrics collection."""
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Create instrumentation for message_bus
    @trace.traced(tracer, name="message_bus")
    async def traced_message_bus(message):
        with tracer.start_as_current_span("process_message") as span:
            span.set_attribute("sender", message.get("sender"))
            span.set_attribute("recipient", message.get("recipient"))
            span.set_attribute("message_size", len(str(message)))

            result = await original_message_bus(message)

            span.set_attribute("processing_success", "error" not in result)
            return result

    return traced_message_bus


@task
async def cherry_agent_task(agent_name, task_data):
    """Wrap agent processing in a Prefect task for monitoring and retry."""
    agent = get_agent(agent_name)
    return await agent.process(task_data)


def create_agent_workflow(workflow_spec):
    """Create a managed workflow across multiple agents."""
    with Flow("cherry_workflow") as flow:
        results = {}
        for step in workflow_spec["steps"]:
            deps = {k: results[k] for k in step.get("dependencies", [])}
            results[step["id"]] = cherry_agent_task(
                step["agent"],
                {"task": step["task"], "dependencies": deps}
            )

    return flow


class VectorKnowledgeStore:
    """Integration with Qdrant vector database for semantic storage and retrieval."""

    def __init__(self, collection_name="cherry_knowledge"):
        self.client = QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536, distance=Distance.COSINE)
            )
