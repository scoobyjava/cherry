from typing import Dict, List, Any, Optional
import re
from datetime import datetime

from cherry.memory.base import BaseMemory


class InMemoryStorage(BaseMemory):
    """
    In-memory implementation of the BaseMemory interface.
    Stores all data in memory using dictionaries.
    """
    
    def __init__(self):
        self._conversations: Dict[str, List[Dict[str, Any]]] = {}
        self._tasks: Dict[str, Dict[str, Any]] = {}
    
    def add_conversation(self, conversation_id: str, messages: List[Dict[str, Any]]) -> None:
        if conversation_id in self._conversations:
            self._conversations[conversation_id].extend(messages)
        else:
            self._conversations[conversation_id] = messages
    
    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        if conversation_id not in self._conversations:
            return []
        return self._conversations[conversation_id]
    
    def list_conversations(self) -> List[str]:
        return list(self._conversations.keys())
    
    def add_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        # Add timestamp if not present
        if 'timestamp' not in task_data:
            task_data['timestamp'] = datetime.now().isoformat()
        
        self._tasks[task_id] = task_data
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        if task_id not in self._tasks:
            return {}
        return self._tasks[task_id]
    
    def list_tasks(self) -> List[str]:
        return list(self._tasks.keys())
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        results = []
        for conversation_id, messages in self._conversations.items():
            for message in messages:
                content = message.get('content', '')
                if isinstance(content, str) and re.search(query, content, re.IGNORECASE):
                    # Add conversation_id to the message for context
                    message_with_context = message.copy()
                    message_with_context['conversation_id'] = conversation_id
                    results.append(message_with_context)
        
        return results
    
    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        results = []
        for task_id, task_data in self._tasks.items():
            task_str = str(task_data)
            if re.search(query, task_str, re.IGNORECASE):
                task_with_id = task_data.copy()
                task_with_id['task_id'] = task_id
                results.append(task_with_id)
        
        return results
    
    def clear(self) -> None:
        self._conversations.clear()
        self._tasks.clear()
