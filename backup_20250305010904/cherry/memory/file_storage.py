import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

from cherry.memory.base import BaseMemory


class FileStorage(BaseMemory):
    """
    File-based implementation of the BaseMemory interface.
    Stores data in JSON files organized by type and ID.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize file storage with a directory path.
        
        Args:
            storage_dir: Directory to store memory files (default: ./cherry_memory)
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "cherry_memory")
        self.conversations_dir = os.path.join(self.storage_dir, "conversations")
        self.tasks_dir = os.path.join(self.storage_dir, "tasks")
        
        # Create directories if they don't exist
        for directory in [self.conversations_dir, self.tasks_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def _get_conversation_path(self, conversation_id: str) -> str:
        return os.path.join(self.conversations_dir, f"{conversation_id}.json")
    
    def _get_task_path(self, task_id: str) -> str:
        return os.path.join(self.tasks_dir, f"{task_id}.json")
    
    def add_conversation(self, conversation_id: str, messages: List[Dict[str, Any]]) -> None:
        file_path = self._get_conversation_path(conversation_id)
        
        existing_messages = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    existing_messages = json.load(f)
            except json.JSONDecodeError:
                # Handle corrupt files by starting fresh
                existing_messages = []
        
        # Append new messages
        existing_messages.extend(messages)
        
        # Write back to file
        with open(file_path, 'w') as f:
            json.dump(existing_messages, f, indent=2)
    
    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        file_path = self._get_conversation_path(conversation_id)
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def list_conversations(self) -> List[str]:
        if not os.path.exists(self.conversations_dir):
            return []
            
        conversations = []
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                conversations.append(filename[:-5])  # Remove .json extension
        
        return conversations
    
    def add_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        # Add timestamp if not present
        if 'timestamp' not in task_data:
            task_data['timestamp'] = datetime.now().isoformat()
            
        file_path = self._get_task_path(task_id)
        
        with open(file_path, 'w') as f:
            json.dump(task_data, f, indent=2)
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        file_path = self._get_task_path(task_id)
        
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def list_tasks(self) -> List[str]:
        if not os.path.exists(self.tasks_dir):
            return []
            
        tasks = []
        for filename in os.listdir(self.tasks_dir):
            if filename.endswith('.json'):
                tasks.append(filename[:-5])  # Remove .json extension
        
        return tasks
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        results = []
        
        for conversation_id in self.list_conversations():
            messages = self.get_conversation(conversation_id)
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
        
        for task_id in self.list_tasks():
            task_data = self.get_task(task_id)
            task_str = json.dumps(task_data)
            if re.search(query, task_str, re.IGNORECASE):
                task_with_id = task_data.copy()
                task_with_id['task_id'] = task_id
                results.append(task_with_id)
        
        return results
    
    def clear(self) -> None:
        # Remove all files but keep the directory structure
        for directory in [self.conversations_dir, self.tasks_dir]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
