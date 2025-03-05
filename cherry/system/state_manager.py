import json
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def sanitize_input(data: Any) -> Any:
    # Basic sanitization: if string, strip and check for unwanted characters
    if isinstance(data, str):
        return data.strip()
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    if isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


class StateManager:
    """
    Manages and persists the current state of Cherry's components
    (active agents, ongoing tasks, chat history, performance metrics).
    """

    def __init__(self):
        self.state: Dict[str, Any] = {
            "active_agents": [],       # List[str]
            "ongoing_tasks": [],       # List[Dict[str, Any]]
            "chat_history": [],        # List[Dict[str, Any]]
            "performance_metrics": {}  # Dict[str, Any]
        }

    def get_state(self) -> Dict[str, Any]:
        return self.state

    def update_state(self, component: str, data: Any) -> None:
        """
        Update a component in the state after sanitizing and validating data.
        """
        data = sanitize_input(data)
        if component not in self.state:
            logger.error(f"Unknown component: {component}")
            return
        # Simple validation: Type check based on existing type.
        current_type = type(self.state[component])
        if not isinstance(data, current_type):
            logger.error(
                f"Invalid data type for {component}. Expected: {current_type.__name__}")
            return
        self.state[component] = data
        logger.info(f"Updated state for {component}")

    def serialize_state(self) -> str:
        """
        Serialize the current state to a JSON string.
        """
        try:
            return json.dumps(self.state)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return ""

    def deserialize_state(self, json_string: str) -> Dict[str, Any]:
        """
        Deserialize a JSON string to update the state.
        Validate that required keys are present and sanitize all inputs.
        """
        try:
            data = json.loads(json_string)
            if not isinstance(data, dict):
                raise ValueError("Deserialized data is not a dictionary")
            # Validate required keys exist; ignore unknown keys.
            required_keys = {"active_agents", "ongoing_tasks",
                             "chat_history", "performance_metrics"}
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing key in state data: {key}")
            sanitized_data = sanitize_input(data)
            self.state.update({k: sanitized_data[k] for k in required_keys})
            logger.info("State successfully deserialized and updated")
            return self.state
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return {}

    def add_chat_message(self, message: Dict[str, Any]) -> None:
        """
        Append a chat message to chat_history after sanitization.
        Expect message to include at least 'timestamp' and 'content'.
        """
        message = sanitize_input(message)
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        self.state["chat_history"].append(message)
        logger.info("Chat message added")
