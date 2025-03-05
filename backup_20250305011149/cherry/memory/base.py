from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union


class BaseMemory(ABC):
    """
    Abstract base class for memory storage implementations.
    Defines interface for storing and retrieving conversation and task data.
    """
    
    @abstractmethod
    def add_conversation(self, conversation_id: str, messages: List[Dict[str, Any]]) -> None:
        """
        Store a conversation or append to existing conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            messages: List of message objects to store
        """
        pass
    
    @abstractmethod
    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve a stored conversation by ID.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of message objects in the conversation
        """
        pass
    
    @abstractmethod
    def list_conversations(self) -> List[str]:
        """
        List all available conversation IDs.
        
        Returns:
            List of conversation IDs
        """
        pass
    
    @abstractmethod
    def add_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """
        Store a task or update an existing task.
        
        Args:
            task_id: Unique identifier for the task
            task_data: Task information to store
        """
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve a stored task by ID.
        
        Args:
            task_id: Unique identifier for the task
            
        Returns:
            Task data dictionary
        """
        pass
    
    @abstractmethod
    def list_tasks(self) -> List[str]:
        """
        List all available task IDs.
        
        Returns:
            List of task IDs
        """
        pass
    
    @abstractmethod
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """
        Search through conversations for relevant content.
        
        Args:
            query: Search terms or criteria
            
        Returns:
            List of matching conversation messages
        """
        pass
    
    @abstractmethod
    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search through tasks for relevant content.
        
        Args:
            query: Search terms or criteria
            
        Returns:
            List of matching tasks
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all stored data."""
        pass
