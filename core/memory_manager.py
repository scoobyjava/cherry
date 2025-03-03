# memory.py
from typing import List, Dict, Any, Optional
import time
import json
import os
from abc import ABC, abstractmethod
from config import Config
from logger import logger

class BaseMemory(ABC):
    """Abstract base class for different memory implementations."""
    
    @abstractmethod
    def add_task(self, task_data: Dict[str, Any]) -> None:
        """Add a task to memory."""
        pass
    
    @abstractmethod
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> None:
        """Update a task in memory."""
        pass
    
    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a task from memory."""
        pass
    
    @abstractmethod
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all tasks from memory."""
        pass
    
    @abstractmethod
    def add_conversation(self, conversation_data: Dict[str, Any]) -> None:
        """Add a conversation exchange to memory."""
        pass
    
    @abstractmethod
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent conversations from memory."""
        pass


class InMemoryStorage(BaseMemory):
    """Simple in-memory implementation of the memory interface."""
    
    def __init__(self):
        self.tasks = {}
        self.conversations = []
        logger.info("Initialized in-memory storage")
    
    def add_task(self, task_data: Dict[str, Any]) -> None:
        """Add a task to memory."""
        task_id = task_data.get("id")
        if task_id is not None:
            self.tasks[task_id] = task_data
            logger.debug(f"Added task {task_id} to memory")
    
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> None:
        """Update a task in memory."""
        if task_id in self.tasks:
            self.tasks[task_id].update(task_data)
            logger.debug(f"Updated task {task_id} in memory")
        else:
            logger.warning(f"Attempted to update non-existent task {task_id}")
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a task from memory."""
        task = self.tasks.get(task_id)
        if task is None:
            logger.warning(f"Task {task_id} not found in memory")
        return task
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all tasks from memory."""
        return list(self.tasks.values())
    
    def add_conversation(self, conversation_data: Dict[str, Any]) -> None:
        """Add a conversation exchange to memory."""
        # Add timestamp if not present
        if "timestamp" not in conversation_data:
            conversation_data["timestamp"] = time.time()
        
        self.conversations.append(conversation_data)
        logger.debug(f"Added conversation to memory, total: {len(self.conversations)}")
        
        # Limit the number of conversations stored in memory
        if len(self.conversations) > Config.MAX_COMPLETED_TASKS:
            self.conversations = self.conversations[-Config.MAX_COMPLETED_TASKS:]
            logger.debug(f"Trimmed conversations to {Config.MAX_COMPLETED_TASKS}")
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent conversations from memory."""
        # Sort by timestamp and return the most recent ones
        sorted_convos = sorted(
            self.conversations, 
            key=lambda x: x.get("timestamp", 0), 
            reverse=True
        )
        return sorted_convos[:limit]


class FileMemoryStorage(BaseMemory):
    """File-based implementation of the memory interface."""
    
    def __init__(self, tasks_file: str = "tasks.json", conversations_file: str = "conversations.json"):
        self.tasks_file = tasks_file
        self.conversations_file = conversations_file
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        # Load existing data
        self.tasks = self._load_tasks()
        self.conversations = self._load_conversations()
        
        logger.info(f"Initialized file-based storage with {len(self.tasks)} tasks and {len(self.conversations)} conversations")
    
    def _initialize_files(self) -> None:
        """Initialize the storage files if they don't exist."""
        if not os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'w') as f:
                json.dump({}, f)
            logger.info(f"Created tasks file: {self.tasks_file}")
        
        if not os.path.exists(self.conversations_file):
            with open(self.conversations_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created conversations file: {self.conversations_file}")
    
    def _load_tasks(self) -> Dict[int, Dict[str, Any]]:
        """Load tasks from file."""
        try:
            with open(self.tasks_file, 'r') as f:
                tasks_data = json.load(f)
                
                # Convert string keys back to integers
                return {int(k): v for k, v in tasks_data.items()}
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            return {}
    
    def _load_conversations(self) -> List[Dict[str, Any]]:
        """Load conversations from file."""
        try:
            with open(self.conversations_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            return []
    
    def _save_tasks(self) -> None:
        """Save tasks to file."""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
    
    def _save_conversations(self) -> None:
        """Save conversations to file."""
        try:
            with open(self.conversations_file, 'w') as f:
                json.dump(self.conversations, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving conversations: {e}")
    
    def add_task(self, task_data: Dict[str, Any]) -> None:
        """Add a task to memory."""
        task_id = task_data.get("id")
        if task_id is not None:
            self.tasks[task_id] = task_data
            self._save_tasks()
            logger.debug(f"Added and saved task {task_id}")
    
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> None:
        """Update a task in memory."""
        if task_id in self.tasks:
            self.tasks[task_id].update(task_data)
            self._save_tasks()
            logger.debug(f"Updated and saved task {task_id}")
        else:
            logger.warning(f"Attempted to update non-existent task {task_id}")
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a task from memory."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all tasks from memory."""
        return list(self.tasks.values())
    
    def add_conversation(self, conversation_data: Dict[str, Any]) -> None:
        """Add a conversation exchange to memory."""
        # Add timestamp if not present
        if "timestamp" not in conversation_data:
            conversation_data["timestamp"] = time.time()
        
        self.conversations.append(conversation_data)
        
        # Limit the number of conversations stored
        if len(self.conversations) > Config.MAX_COMPLETED_TASKS:
            self.conversations = self.conversations[-Config.MAX_COMPLETED_TASKS:]
        
        self._save_conversations()
        logger.debug("Added and saved new conversation")
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent conversations from memory."""
        # Sort by timestamp and return the most recent ones
        sorted_convos = sorted(
            self.conversations, 
            key=lambda x: x.get("timestamp", 0), 
            reverse=True
        )
        return sorted_convos[:limit]


# Create the appropriate memory storage based on configuration
def create_memory_storage() -> BaseMemory:
    """Factory function to create the appropriate memory storage."""
    storage_type = Config.DB_TYPE.lower()
    
    if storage_type == "file":
        return FileMemoryStorage()
    else:  # Default to in-memory
        return InMemoryStorage()

# Initialize the memory storage
memory_storage = create_memory_storage()