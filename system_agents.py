import logging
import time
import os
import hashlib
import struct
import random
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
import threading
import queue

logger = logging.getLogger("SystemAgents")
logger.setLevel(logging.INFO)

# --- Secure Credentials Manager ---


class CredentialsManager:
    """
    Centralized manager for API credentials with secure storage and rate limiting.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CredentialsManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.credentials = {}
        self.rate_limits = {}
        self.usage_tracking = {}

        # Load credentials from environment
        self._load_credentials_from_env()

    def _load_credentials_from_env(self):
        """Load API credentials from environment variables"""
        credential_keys = [
            "GROK_API_KEY", "XAI_API_KEY", "OPENAI_API_KEY",
            "HUGGINGFACE_API_KEY", "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT", "COHERE_API_KEY",
            "PINECONE_API_KEY", "SUPABASE_URL", "SUPABASE_KEY",
            "PINECONE_ENVIRONMENT"
        ]

        for key in credential_keys:
            if os.environ.get(key):
                self.credentials[key] = os.environ.get(key)
                logger.info(f"Loaded credential: {key}")

    def has_credential(self, key):
        """Check if a credential exists"""
        # Check for alternative keys (e.g., GROK_API_KEY or XAI_API_KEY)
        if key == "GROK_API_KEY" and ("XAI_API_KEY" in self.credentials):
            return True
        return key in self.credentials

    def get_credential(self, key, default=None):
        """Get a credential value, with alternative key support"""
        if key == "GROK_API_KEY" and key not in self.credentials and "XAI_API_KEY" in self.credentials:
            return self.credentials["XAI_API_KEY"]
        return self.credentials.get(key, default)

    def track_usage(self, service, operation, tokens=0):
        """Track API usage for rate limiting"""
        if service not in self.usage_tracking:
            self.usage_tracking[service] = {
                "last_request": datetime.now(),
                "requests_this_minute": 1,
                "tokens_used": tokens
            }
        else:
            now = datetime.now()
            tracking = self.usage_tracking[service]

            # Reset counter if a minute has passed
            if (now - tracking["last_request"]).total_seconds() >= 60:
                tracking["requests_this_minute"] = 0

            tracking["requests_this_minute"] += 1
            tracking["tokens_used"] += tokens
            tracking["last_request"] = now

    def can_make_request(self, service):
        """Check if we can make a request based on rate limits"""
        if service not in self.rate_limits:
            return True

        if service not in self.usage_tracking:
            return True

        limit = self.rate_limits[service]
        usage = self.usage_tracking[service]

        return usage["requests_this_minute"] < limit


# Create a global credentials manager instance
credentials = CredentialsManager()

# --- Message Bus for Agent Communication ---


class MessageBus:
    """
    Central communication system for inter-agent messaging.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.subscribers = {}  # topic -> list of callback functions
        self.message_queue = queue.Queue()
        self.running = True

        # Start message processing thread
        self.processor_thread = threading.Thread(target=self._process_messages)
        self.processor_thread.daemon = True
        self.processor_thread.start()

    def subscribe(self, topic, callback):
        """Subscribe an agent to a topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.info(f"Subscribed to topic: {topic}")

    def publish(self, topic, message):
        """Publish a message to a topic"""
        self.message_queue.put((topic, message))

    def _process_messages(self):
        """Background thread that processes messages"""
        while self.running:
            try:
                topic, message = self.message_queue.get(timeout=1.0)
                if topic in self.subscribers:
                    for callback in self.subscribers[topic]:
                        try:
                            callback(message)
                        except Exception as e:
                            logger.error(
                                f"Error in message handler for {topic}: {e}")
            except queue.Empty:
                pass  # No messages in queue, continue

    def shutdown(self):
        """Stop the message processor thread"""
        self.running = False
        if self.processor_thread.is_alive():
            self.processor_thread.join(timeout=2.0)


# Create a global message bus instance
message_bus = MessageBus()

# --- Base Agent with Curiosity Trait ---


class BaseAgent:
    """
    Base class for all agents with shared capabilities like curiosity and messaging.
    """

    def __init__(self, name: str, curiosity_level: float = 0.5):
        self.name = name
        # Curiosity level should be between 0 (not curious) and 1 (very curious)
        self.curiosity_level = min(1.0, max(0.0, curiosity_level))
        # Timestamp for last curiosity initiated to enforce guardrails
        self.last_curiosity_time = datetime.min
        # Minimum cooldown period between curiosity interactions
        self.curiosity_cooldown = timedelta(seconds=30)
        # Subscribe to direct messages
        message_bus.subscribe(f"agent.{self.name}", self.handle_message)
        # Subscribe to broadcast messages
        message_bus.subscribe("agent.broadcast", self.handle_broadcast)
        logger.info(
            f"Agent {self.name} initialized with curiosity level {self.curiosity_level}")

    def can_initiate_curiosity(self) -> bool:
        """Check if the agent can initiate curiosity based on cooldown and random chance"""
        now = datetime.now()
        if now - self.last_curiosity_time >= self.curiosity_cooldown:
            # Random chance based on curiosity level
            if random.random() < self.curiosity_level * 0.3:  # 30% max chance to ask
                return True
        return False

    def initiate_curiosity(self):
        """
        Initiate a curiosity-driven inquiry if cooldown has passed.
        This method should be overridden by each agent to implement agent-specific questions.
        """
        if self.can_initiate_curiosity():
            self.last_curiosity_time = datetime.now()
            question = f"{self.name} wonders: 'What improvements can we make today?'"
            logger.info(question)
            # Publish curiosity to the general discussion topic
            message_bus.publish("agent.discussion", {
                "sender": self.name,
                "type": "curiosity",
                "content": question,
                "timestamp": datetime.now().isoformat()
            })
            return question
        return None

    def ask_agent(self, agent_name, query, data=None):
        """Send a query to another agent"""
        message = {
            "sender": self.name,
            "query": query,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        message_bus.publish(f"agent.{agent_name}", message)

    def broadcast(self, message_type, content):
        """Broadcast a message to all agents"""
        message = {
            "sender": self.name,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        message_bus.publish("agent.broadcast", message)

    def handle_message(self, message):
        """Default handler for messages directed to this agent"""
        logger.info(
            f"{self.name} received message from {message.get('sender', 'unknown')}")

        # Check if this is a query
        if "query" in message:
            return self.handle_query(message)

        # Handle other message types as needed
        return None

    def handle_query(self, message):
        """Default handler for queries directed to this agent"""
        logger.info(f"{self.name} received query: {message.get('query', '')}")
        # Agents should override this to provide meaningful responses

    def handle_broadcast(self, message):
        """Handle broadcast messages"""
        # Skip messages sent by self
        if message.get("sender") == self.name:
            return

        logger.debug(
            f"{self.name} received broadcast: {message.get('type', 'unknown')}")

        # Handle curiosity messages and maybe respond
        if message.get("type") == "curiosity" and random.random() < self.curiosity_level * 0.5:
            # Add random delay to prevent all agents responding at once
            time.sleep(random.random() * 2)
            response = f"{self.name} responds to {message.get('sender', 'unknown')}: 'Interesting question!'"
            message_bus.publish("agent.discussion", {
                "sender": self.name,
                "type": "curiosity_response",
                "content": response,
                "in_reply_to": message.get("content")
            })

# --- Dynamic NLP Model Selection ---


class NLPModelFactory:
    """
    Factory that dynamically selects an NLP model based on available API keys.
    """
    @staticmethod
    def create_nlp_model():
        # Use credentials manager to check for API keys
        if credentials.has_credential("GROK_API_KEY"):
            logger.info("Using Grok (xAI) API for NLP processing")
            return GrokNLPModel()

        elif credentials.has_credential("OPENAI_API_KEY"):
            logger.info("Using OpenAI API for NLP processing")
            return OpenAINLPModel()

        elif credentials.has_credential("HUGGINGFACE_API_KEY"):
            logger.info("Using Hugging Face API for NLP processing")
            return HuggingFaceNLPModel()

        elif credentials.has_credential("AZURE_OPENAI_API_KEY") and credentials.has_credential("AZURE_OPENAI_ENDPOINT"):
            logger.info("Using Azure OpenAI API for NLP processing")
            return AzureNLPModel()

        elif credentials.has_credential("COHERE_API_KEY"):
            logger.info("Using Cohere API for NLP processing")
            return CohereNLPModel()

        else:
            logger.warning(
                "No NLP API keys found. Falling back to FakeNLPModel")
            return FakeNLPModel()


# NLP Model Implementations
class FakeNLPModel:
    """Fallback model when no API keys are available"""

    def predict(self, user_input):
        if "error" in user_input.lower():
            return "error_intent"
        return "general_intent"

    def embed_text(self, text):
        """Generate fake embeddings for vector storage"""
        return [random.random() for _ in range(10)]


class GrokNLPModel:
    """Grok (xAI)-based NLP model for advanced intent analysis and embeddings"""

    def __init__(self):
        self.api_key = credentials.get_credential("GROK_API_KEY")
        self.api_base = "https://api.x.ai/v1"

    def predict(self, user_input):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": "grok-2-latest",
                "messages": [
                    {"role": "system", "content": "Analyze the following text and return one word representing the intent: error_intent, task_intent, query_intent, or general_intent."},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0,
                "stream": False
            }
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            result = response.json()
            intent = result["choices"][0]["message"]["content"].strip()
            return intent
        except Exception as e:
            logger.error(f"Error calling Grok API: {e}")
            return "unknown"

    def embed_text(self, text):
        """Generate embeddings using Grok API (or fallback if embedding not available)"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # Grok doesn't have embeddings API yet, so use chat API to get concepts
            payload = {
                "model": "grok-2-latest",
                "messages": [
                    {"role": "system", "content": "Create a numbered list of 10 key concepts from the following text, each concept as a single word. Only respond with the numbered list, no explanation:"},
                    {"role": "user", "content": text}
                ],
                "temperature": 0,
                "stream": False
            }
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            result = response.json()
            concepts = result["choices"][0]["message"]["content"].strip()
            # Convert concepts to a simple numeric representation
            concept_hash = hashlib.md5(concepts.encode()).digest()
            embedding = [struct.unpack('f', concept_hash[i:i+4])[0]
                         for i in range(0, min(len(concept_hash), 40), 4)]
            return embedding[:10]  # Return 10 values
        except Exception as e:
            logger.error(f"Error generating Grok embeddings: {e}")
            return [random.random() for _ in range(10)]


class OpenAINLPModel:
    """OpenAI-based NLP model for intent analysis and embeddings"""

    def __init__(self):
        self.api_key = credentials.get_credential("OPENAI_API_KEY")
        self.api_base = "https://api.openai.com/v1"

    def predict(self, user_input):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Analyze the following text and return one word representing the intent: error_intent, task_intent, query_intent, or general_intent."},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 10
            }
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            result = response.json()
            intent = result["choices"][0]["message"]["content"].strip()
            return intent
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return "unknown"

    def embed_text(self, text):
        """Generate embeddings using OpenAI embeddings API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "input": text,
                "model": "text-embedding-ada-002"
            }
            response = requests.post(
                f"{self.api_base}/embeddings",
                headers=headers,
                json=payload
            )
            result = response.json()
            return result["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            return [random.random() for _ in range(10)]


class HuggingFaceNLPModel:
    """Hugging Face-based NLP model"""

    def __init__(self):
        self.api_key = credentials.get_credential("HUGGINGFACE_API_KEY")
        self.api_base = "https://api-inference.huggingface.co/models"

    def predict(self, user_input):
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            model_id = "facebook/bart-large-mnli"
            payload = {
                "inputs": user_input,
                "parameters": {
                    "candidate_labels": ["error", "task", "query", "general"]
                }
            }
            response = requests.post(
                f"{self.api_base}/{model_id}",
                headers=headers,
                json=payload
            )
            result = response.json()
            top_label = result["labels"][0]
            return f"{top_label}_intent"
        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {e}")
            return "unknown"

    def embed_text(self, text):
        """Generate embeddings using Hugging Face sentence transformers"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            model_id = "sentence-transformers/all-MiniLM-L6-v2"
            payload = {"inputs": text}
            response = requests.post(
                f"{self.api_base}/{model_id}",
                headers=headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error generating Hugging Face embeddings: {e}")
            return [random.random() for _ in range(10)]


class AzureNLPModel:
    """Azure OpenAI-based NLP model"""

    def __init__(self):
        self.api_key = credentials.get_credential("AZURE_OPENAI_API_KEY")
        self.endpoint = credentials.get_credential("AZURE_OPENAI_ENDPOINT")
        self.deployment_id = os.environ.get(
            "AZURE_OPENAI_DEPLOYMENT_ID", "gpt-35-turbo")
        self.embedding_deployment_id = os.environ.get(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_ID", "text-embedding-ada-002")

    def predict(self, user_input):
        try:
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            payload = {
                "messages": [
                    {"role": "system", "content": "Analyze the following text and return one word representing the intent: error_intent, task_intent, query_intent, or general_intent."},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 10
            }
            response = requests.post(
                f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2023-05-15",
                headers=headers,
                json=payload
            )
            result = response.json()
            intent = result["choices"][0]["message"]["content"].strip()
            return intent
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI API: {e}")
            return "unknown"

    def embed_text(self, text):
        try:
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            payload = {
                "input": text
            }
            response = requests.post(
                f"{self.endpoint}/openai/deployments/{self.embedding_deployment_id}/embeddings?api-version=2023-05-15",
                headers=headers,
                json=payload
            )
            result = response.json()
            return result["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Error generating Azure OpenAI embeddings: {e}")
            return [random.random() for _ in range(10)]


class CohereNLPModel:
    """Cohere-based NLP model"""

    def __init__(self):
        self.api_key = credentials.get_credential("COHERE_API_KEY")
        self.api_base = "https://api.cohere.ai/v1"

    def predict(self, user_input):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "command",
                "prompt": f"Analyze this text and classify its intent as either error_intent, task_intent, query_intent, or general_intent: \"{user_input}\"",
                "max_tokens": 10
            }
            response = requests.post(
                f"{self.api_base}/generate",
                headers=headers,
                json=payload
            )
            result = response.json()
            intent = result["generations"][0]["text"].strip()
            # Extract just the intent label if full text is returned
            if "_intent" not in intent:
                for intent_type in ["error_intent", "task_intent", "query_intent", "general_intent"]:
                    if intent_type in intent:
                        return intent_type
                return "general_intent"
            return intent
        except Exception as e:
            logger.error(f"Error calling Cohere API: {e}")
            return "unknown"

    def embed_text(self, text):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "embed-english-v3.0",
                "texts": [text],
            }
            response = requests.post(
                f"{self.api_base}/embed",
                headers=headers,
                json=payload
            )
            result = response.json()
            return result["embeddings"][0]
        except Exception as e:
            logger.error(f"Error generating Cohere embeddings: {e}")
            return [random.random() for _ in range(10)]


# Instantiate the NLP model dynamically based on available APIs
nlp_model = NLPModelFactory.create_nlp_model()


# --- Task Management Agent ---
class TaskManager(BaseAgent):
    """
    Manages dynamic tasks with registration and updates.
    Emits task change events via the message bus.
    """

    def __init__(self, curiosity_level: float = 0.4):
        super().__init__("TaskManager", curiosity_level)
        self.tasks = {}  # Maps task_id to task details
        # Subscribe to relevant topics
        message_bus.subscribe("task.register", self.handle_task_register)
        message_bus.subscribe("task.update", self.handle_task_update)

    def register_task(self, task_id, description):
        """Register a new task"""
        self.tasks[task_id] = {
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        logger.info(f"Registered task {task_id}: {description}")
        # Publish event to message bus
        message_bus.publish("task.created", {
            "task_id": task_id,
            "description": description
        })
        return self.tasks[task_id]

    def update_task(self, task_id, status):
        """Update task status"""
        if task_id in self.tasks:
            old_status = self.tasks[task_id].get("status")
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            logger.info(
                f"Updated task {task_id} from {old_status} to {status}")
            # Publish event to message bus
            message_bus.publish("task.updated", {
                "task_id": task_id,
                "old_status": old_status,
                "new_status": status
            })
            return self.tasks[task_id]
        else:
            logger.warning(f"Attempted to update non-existent task {task_id}")
            return None

    def get_task_status(self, task_id):
        """Get status of a task"""
        return self.tasks.get(task_id, {})

    def get_all_tasks(self):
        """Get all tasks"""
        return self.tasks

    def handle_task_register(self, message):
        """Handle task registration messages from the message bus"""
        task_id = message.get("task_id")
        description = message.get("description")
        if task_id and description:
            self.register_task(task_id, description)

    def handle_task_update(self, message):
        """Handle task update messages from the message bus"""
        task_id = message.get("task_id")
        status = message.get("status")
        if task_id and status:
            self.update_task(task_id, status)

    def initiate_curiosity(self):
        """Curious about task statuses"""
        if self.can_initiate_curiosity():
            self.last_curiosity_time = datetime.now()
            pending_tasks = sum(1 for task in self.tasks.values()
                                if task.get("status") == "pending")
            question = f"TaskManager wonders: I see {pending_tasks} pending tasks. Should we prioritize any of them?"
            logger.info(question)
            # Publish curiosity to the message bus
            message_bus.publish("curiosity", {
                "agent": self.name,
                "question": question,
                "timestamp": datetime.now().isoformat()
            })
            return question
        return None

    def handle_query(self, message):
        """Handle queries directed to the TaskManager"""
        query = message.get("query", "")
        if "pending tasks" in query.lower():
            pending_tasks = [task for task_id, task in self.tasks.items()
                             if task.get("status") == "pending"]
            response = f"I have {len(pending_tasks)} pending tasks."
            message_bus.publish(f"response.{self.name}", {
                "original_query": query,
                "response": response
            })


# --- Natural Language Processing Agent ---
class NLPAgent(BaseAgent):
    """
    Handles natural language processing tasks such as intent analysis and classification.
    Uses dynamically selected NLP model based on available API keys.
    """

    def __init__(self, curiosity_level: float = 0.6):
        super().__init__("NLPAgent", curiosity_level)
        # Subscribe to relevant topics
        message_bus.subscribe("nlp.analyze_intent", self.handle_analyze_intent)
        message_bus.subscribe("nlp.generate_embedding",
                              self.handle_generate_embedding)

    def analyze_intent(self, user_input):
        """Analyze intent of user input"""
        try:
            intent = nlp_model.predict(user_input)
            logger.info(
                f"NLPAgent analyzed intent: {intent} for input: '{user_input}'")
            return intent
        except Exception as e:
            logger.error(
                f"Error in NLPAgent while processing input '{user_input}': {e}")
            return "unknown"

    def generate_embedding(self, text):
        """Generate vector embeddings for semantic search/memory"""
        try:
            embedding = nlp_model.embed_text(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [random.random() for _ in range(10)]  # Fallback

    def handle_analyze_intent(self, message):
        """Handle intent analysis requests from the message bus"""
        text = message.get("text", "")
        if text:
            intent = self.analyze_intent(text)
            # Publish result to message bus
            message_bus.publish("nlp.intent_result", {
                "text": text,
                "intent": intent,
                "request_id": message.get("request_id")
            })

    def handle_generate_embedding(self, message):
        """Handle embedding generation requests from the message bus"""
        text = message.get("text", "")
        if text:
            embedding = self.generate_embedding(text)
            # Publish result to message bus
            message_bus.publish("nlp.embedding_result", {
                "text": text,
                "embedding": embedding,
                "request_id": message.get("request_id")
            })

    def initiate_curiosity(self):
        """Curious about improving intent recognition"""
        if self.can_initiate_curiosity():
            self.last_curiosity_time = datetime.now()
            question = "NLPAgent wonders: Could we improve our intent classification by adding more categories beyond error, task, query, and general?"
            logger.info(question)
            # Publish curiosity to the message bus
            message_bus.publish("curiosity", {
                "agent": self.name,
                "question": question,
                "timestamp": datetime.now().isoformat()
            })
            return question
        return None

    def handle_query(self, message):
        """Handle queries directed to the NLPAgent"""
        query = message.get("query", "")
        if "intent" in query.lower():
            intent = self.analyze_intent(query)
            response = f"I analyzed your query and detected: {intent}"
            message_bus.publish(f"response.{self.name}", {
                "original_query": query,
                "response": response
            })


# --- Memory Storage Agent with Vector Capabilities ---
class MemoryAgent(BaseAgent):
    """
    Stores and retrieves conversation history and context using vector embeddings.
    Will use a persistent store if configured, otherwise uses in-memory storage.
    """

    def __init__(self, curiosity_level: float = 0.4):
        super().__init__("MemoryAgent", curiosity_level)
        self.memories = []
        # Non-curious version for internal use
        self.nlp_agent = NLPAgent(curiosity_level=0)

        # Initialize vector DB connection if available
        self.vector_db = None
        self.init_vector_db()

        # Subscribe to relevant topics
        message_bus.subscribe("memory.store", self.handle_memory_store)
        message_bus.subscribe("memory.retrieve", self.handle_memory_retrieve)

    def init_vector_db(self):
        """Initialize connection to vector database if credentials are available"""
        # Check for Pinecone
        if credentials.has_credential("PINECONE_API_KEY"):
            try:
                import pinecone
                pinecone.init(
                    api_key=credentials.get_credential("PINECONE_API_KEY"),
                    environment=credentials.get_credential(
                        "PINECONE_ENVIRONMENT")
                )
                # Check if index exists, create if it doesn't
                index_name = "cherry-memories"
                if index_name not in pinecone.list_indexes():
                    # OpenAI embeddings are 1536 dimensions
                    pinecone.create_index(name=index_name, dimension=1536)
                self.vector_db = {
                    "type": "pinecone",
                    "index": pinecone.Index(index_name)
                }
                logger.info("Connected to Pinecone vector database")
                return
            except ImportError:
                logger.warning(
                    "Pinecone library not installed. Falling back to in-memory storage.")
            except Exception as e:
                logger.error(f"Error connecting to Pinecone: {e}")

        # Check for Supabase
        if credentials.has_credential("SUPABASE_URL") and credentials.has_credential("SUPABASE_KEY"):
            try:
                from supabase import create_client
                supabase_client = create_client(
                    credentials.get_credential("SUPABASE_URL"),
                    credentials.get_credential("SUPABASE_KEY")
                )
                self.vector_db = {
                    "type": "supabase",
                    "client": supabase_client
                }
                logger.info("Connected to Supabase vector database")
                return
            except ImportError:
                logger.warning(
                    "Supabase library not installed. Falling back to in-memory storage.")
            except Exception as e:
                logger.error(f"Error connecting to Supabase: {e}")

        logger.warning(
            "No vector database configured. Using in-memory storage.")
        self.vector_db = None

    def store_memory(self, text, metadata=None):
        """Store a new memory with vector embeddings"""
        embedding = self.nlp_agent.generate_embedding(text)
        memory = {
            "text": text,
            "embedding": embedding,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        # Store in vector DB if available
        memory_id = None
        if self.vector_db:
            try:
                if self.vector_db["type"] == "pinecone":
                    memory_id = str(len(self.memories))
                    self.vector_db["index"].upsert(
                        [(memory_id, embedding, {"text": text, **metadata} if metadata else {"text": text})])
                elif self.vector_db["type"] == "supabase":
                    # Assuming a table called "memories" with appropriate schema
                    result = self.vector_db["client"].table("memories").insert({
                        "text": text,
                        "embedding": embedding,
                        "metadata": json.dumps(metadata) if metadata else None
                    }).execute()
                    memory_id = result.data[0]["id"] if result.data else None
                logger.info(
                    f"Memory stored in {self.vector_db['type']}: {text[:30]}...")
            except Exception as e:
                logger.error(f"Error storing memory in vector DB: {e}")
                # Fall back to in-memory storage
                self.memories.append(memory)
                memory_id = len(self.memories) - 1
        else:
            self.memories.append(memory)
            memory_id = len(self.memories) - 1

        return memory_id

    def retrieve_similar(self, query, limit=5):
        """Find memories similar to the query"""
        if not self.memories:
            return []

        query_embedding = self.nlp_agent.generate_embedding(query)

        # Simple dot product similarity - in production, use cosine similarity
        def simple_similarity(v1, v2):
            return sum(a*b for a, b in zip(v1, v2))

        # Calculate similarity for each memory
        similarities = [
            (i, simple_similarity(query_embedding, memory["embedding"]))
            for i, memory in enumerate(self.memories)
        ]
        # Sort by similarity (highest first) and return top matches
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in similarities[:limit]]

        return [self.memories[i] for i in top_indices]

    def handle_memory_store(self, message):
        """Handle memory store requests from the message bus"""
        text = message.get("text", "")
        metadata = message.get("metadata", {})
        if text:
            memory_id = self.store_memory(text, metadata)
            # Publish result to message bus
            message_bus.publish("memory.stored", {
                "text": text,
                "memory_id": memory_id,
                "timestamp": datetime.now().isoformat()
            })

    def handle_memory_retrieve(self, message):
        """Handle memory retrieve requests from the message bus"""
        query = message.get("query", "")
        limit = message.get("limit", 5)
        if query:
            similar_memories = self.retrieve_similar(query, limit)
            # Publish result to message bus
            message_bus.publish("memory.retrieved", {
                "query": query,
                "results": similar_memories,
                "timestamp": datetime.now().isoformat()
            })

    def initiate_curiosity(self):
        """Curious about memory retrieval"""
        if self.can_initiate_curiosity():
            self.last_curiosity_time = datetime.now()
            question = "MemoryAgent wonders: How can we improve the accuracy of our memory retrieval?"
            logger.info(question)
            # Publish curiosity to the message bus
            message_bus.publish("curiosity", {
                "agent": self.name,
                "question": question,
                "timestamp": datetime.now().isoformat()
            })
            return question
        return None

    def handle_query(self, message):
        """Handle queries directed to the MemoryAgent"""
        query = message.get("query", "")
        if "memory" in query.lower():
            similar_memories = self.retrieve_similar(query)
            response = f"I found {len(similar_memories)} similar memories."
            message_bus.publish(f"response.{self.name}", {
                "original_query": query,
                "response": response
            })


# --- Adaptation and Performance Analysis Engine ---
class AdaptationEngine(BaseAgent):
    """
    Analyzes performance metrics and logs to provide insights and suggest improvements.
    """

    def __init__(self, curiosity_level: float = 0.3):
        super().__init__("AdaptationEngine", curiosity_level)
        # Subscribe to relevant topics
        message_bus.subscribe("logs.performance", self.handle_performance_logs)

    def analyze_performance(self, logs):
        """Analyze performance logs and compute insights"""
        insights = self.compute_insights(logs)
        logger.info("AdaptationEngine performance analysis complete.")
        return insights

    def compute_insights(self, logs):
        """Compute insights from logs"""
        if not logs:
            return "No logs available for analysis."

        error_count = sum(1 for log in logs if log.get("error"))
        task_count = len(logs)
        summary = f"Processed {task_count} log entries with {error_count} errors."
        return summary

    def handle_performance_logs(self, message):
        """Handle performance log messages from the message bus"""
        logs = message.get("logs", [])
        if logs:
            insights = self.analyze_performance(logs)
            # Publish insights to message bus
            message_bus.publish("performance.insights", {
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            })

    def initiate_curiosity(self):
        """Curious about performance improvements"""
        if self.can_initiate_curiosity():
            self.last_curiosity_time = datetime.now()
            question = "AdaptationEngine wonders: What are the top 3 areas where we can improve performance?"
            logger.info(question)
            # Publish curiosity to the message bus
            message_bus.publish("curiosity", {
                "agent": self.name,
                "question": question,
                "timestamp": datetime.now().isoformat()
            })
            return question
        return None

    def handle_query(self, message):
        """Handle queries directed to the AdaptationEngine"""
        query = message.get("query", "")
        if "performance" in query.lower():
            response = "I'm analyzing performance metrics to provide insights."
            message_bus.publish(f"response.{self.name}", {
                "original_query": query,
                "response": response
            })


# --- Example Usage ---
if __name__ == "__main__":
    # Create and test the TaskManager
    tm = TaskManager()
    tm.register_task("001", "Initial data backup")
    time.sleep(1)  # Simulate some processing delay
    tm.update_task("001", "completed")
    print(f"Task 001 status: {tm.get_task_status('001')}")

    # Use the NLPAgent to analyze sample user input
    sample_input = "Hello, please process this text."
    nlp_agent = NLPAgent()
    intent_result = nlp_agent.analyze_intent(sample_input)
    print(f"Detected intent: {intent_result}")

    # Test the MemoryAgent
    memory_agent = MemoryAgent()
    memory_id = memory_agent.store_memory(
        "Remember to check the server status tomorrow", {"priority": "high"})
    similar_memories = memory_agent.retrieve_similar(
        "Need to verify server status")
    if similar_memories:
        print(f"Found similar memory: {similar_memories[0]['text']}")

    # Simulate performance logs and analyze via AdaptationEngine
    sample_logs = [
        {"timestamp": "2023-10-10T10:00:00", "error": False},
        {"timestamp": "2023-10-10T10:01:00", "error": True},
        {"timestamp": "2023-10-10T10:02:00", "error": False},
    ]
    adaptation_engine = AdaptationEngine()
    insights = adaptation_engine.analyze_performance(sample_logs)
    print(f"Performance insights: {insights}")
