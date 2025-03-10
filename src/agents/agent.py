#!/usr/bin/env python3
# filepath: /workspaces/cherry/cherry/agent.py

import json
import os
import sys
import re
import time
import uuid
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Agent")

# Import APIManager if available
try:
    from .api import APIManager
except ImportError:
    logger.warning("APIManager import failed. Some features may be unavailable.")
    APIManager = None

class Agent:
    """
    Base Agent class that handles task execution, planning, and tool usage.
    
    The Agent serves as the orchestration layer, managing workflows and
    coordinating between different components of the system.
    """
    
    def __init__(self, config: Dict = None, agent_id: str = None):
        """
        Initialize the agent with configuration and unique ID.
        
        Args:
            config: Dictionary containing agent configuration
            agent_id: Unique identifier for this agent instance
        """
        self.config = config or {}
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.api_manager = None
        self.memory = {}
        self.tools = {}
        self.task_history = []
        self.initialized = False
        self.logs = []
        
        # Security patterns to detect in inputs and outputs
        self.sensitive_patterns = [
            r'([\'"](?:api[_-]?key|api[_-]?secret|password|secret|token|key)[\'"]?\s*[:=]\s*[\'"])[^\'"]+([\'"])',
            r'([\'"](?:ACCESS[_-]?KEY|SECRET[_-]?KEY)[\'"]?\s*[:=]\s*[\'"])[^\'"]+([\'"])',
            r'([\'"](?:GITHUB[_-]?TOKEN)[\'"]?\s*[:=]\s*[\'"])[^\'"]+([\'"])'
        ]
        
        # Register basic tools
        self.register_tool("fetch_knowledge", self._fetch_knowledge)
        self.register_tool("store_knowledge", self._store_knowledge)
        self.register_tool("analyze_text", self._analyze_text)
        
        logger.info(f"Agent {self.agent_id} initialized")

    def initialize(self) -> bool:
        """Initialize the agent and its components"""
        try:
            # Initialize API manager if available
            if APIManager is not None:
                self.api_manager = APIManager(self.config.get("api_config", {}))
                logger.info("API Manager initialized")
            
            # Load persistent memory if available
            memory_path = self.config.get("memory_path")
            if memory_path and os.path.exists(memory_path):
                with open(memory_path, 'r') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded {len(self.memory)} memory items")
            
            self.initialized = True
            self.log("Agent initialization complete")
            return True
        except Exception as e:
            logger.error(f"Initialization error: {str(e)}")
            return False

    def register_tool(self, tool_name: str, tool_function: Callable) -> None:
        """
        Register a new tool for the agent to use
        
        Args:
            tool_name: Name of the tool
            tool_function: Function implementing the tool
        """
        self.tools[tool_name] = tool_function
        logger.info(f"Registered tool: {tool_name}")
    
    def execute_task(self, task: Dict) -> Dict:
        """
        Execute a task based on its type and parameters
        
        Args:
            task: Dictionary containing task information
            
        Returns:
            Dictionary containing task results
        """
        if not self.initialized and not self.initialize():
            return {"success": False, "error": "Agent not initialized"}
        
        task_id = task.get("id", str(uuid.uuid4()))
        task_type = task.get("type", "unknown")
        task_params = task.get("params", {})
        
        # Validate and sanitize input
        if not self._validate_task_input(task_params):
            return {
                "success": False, 
                "error": "Security validation failed. Potentially unsafe input detected.",
                "task_id": task_id
            }
            
        self.log(f"Executing task {task_id} of type {task_type}")
        
        start_time = time.time()
        result = {"success": False, "task_id": task_id, "type": task_type}
        
        try:
            # Execute task based on type
            if task_type == "process_text":
                result = self._process_text_task(task_params)
            elif task_type == "analyze_code":
                result = self._analyze_code_task(task_params)
            elif task_type == "generate_component":
                result = self._generate_component_task(task_params)
            elif task_type == "tool_execution":
                result = self._execute_tool_task(task_params)
            elif task_type == "llm_request":
                result = self._handle_llm_request(task_params)
            else:
                result["error"] = f"Unknown task type: {task_type}"
                
            # Sanitize output
            result = self._sanitize_output(result)
                
        except Exception as e:
            logger.exception(f"Error executing task {task_id}")
            result["error"] = f"Task execution failed: {str(e)}"
            
        # Record execution time
        execution_time = time.time() - start_time
        result["execution_time"] = execution_time
        
        # Add to task history
        task_record = {
            "id": task_id,
            "type": task_type,
            "timestamp": datetime.now().isoformat(),
            "execution_time": execution_time,
            "success": result.get("success", False)
        }
        self.task_history.append(task_record)
        
        self.log(f"Task {task_id} completed in {execution_time:.2f}s - Success: {result.get('success', False)}")
        return result
    
    def _process_text_task(self, params: Dict) -> Dict:
        """Process text analysis tasks"""
        text = params.get("text", "")
        if not text:
            return {"success": False, "error": "No text provided"}
            
        analysis_type = params.get("analysis_type", "general")
        
        # Use API manager to get appropriate language model
        if self.api_manager:
            llm = self.api_manager.select_llm(analysis_type)
            result = llm.execute({"text": text, "type": analysis_type})
            return {"success": True, "analysis": result}
        else:
            # Fallback basic text analysis
            word_count = len(text.split())
            sentiment = self._basic_sentiment(text)
            return {
                "success": True, 
                "analysis": {
                    "word_count": word_count,
                    "sentiment": sentiment,
                    "summary": f"Text contains {word_count} words with {sentiment} sentiment."
                }
            }
    
    def _basic_sentiment(self, text: str) -> str:
        """Very basic sentiment analysis fallback"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "poor", "disappointing"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _analyze_code_task(self, params: Dict) -> Dict:
        """Analyze code for quality and security issues"""
        code = params.get("code", "")
        if not code:
            return {"success": False, "error": "No code provided"}
            
        # Security check
        security_issues = self._check_code_security(code)
        
        # Quality check
        quality_issues = self._check_code_quality(code)
        
        return {
            "success": True,
            "analysis": {
                "security_issues": security_issues,
                "quality_issues": quality_issues,
                "security_score": 10 - min(10, len(security_issues)),
                "quality_score": 10 - min(10, len(quality_issues)),
                "safe_to_deploy": len(security_issues) == 0
            }
        }
    
    def _check_code_security(self, code: str) -> List[Dict]:
        """Check code for security issues"""
        issues = []
        
        # Check for sensitive information
        for pattern in self.sensitive_patterns:
            for match in re.finditer(pattern, code):
                issues.append({
                    "type": "sensitive_data",
                    "description": "Potential sensitive data found",
                    "severity": "high",
                    # Redact the actual sensitive data in the report
                    "snippet": code[max(0, match.start() - 20):match.start()] + 
                              "[REDACTED]" +
                              code[match.end():min(len(code), match.end() + 20)]
                })
        
        # Check for other security patterns
        security_checks = [
            {
                "pattern": r"eval\s*\(",
                "description": "Potentially unsafe eval() usage",
                "severity": "high"
            },
            {
                "pattern": r"(?:exec|system|popen|subprocess\.call)\s*\(",
                "description": "Potential command injection",
                "severity": "high"
            },
            {
                "pattern": r"innerHTML|outerHTML",
                "description": "Potential XSS vulnerability",
                "severity": "medium"
            }
        ]
        
        for check in security_checks:
            for match in re.finditer(check["pattern"], code):
                issues.append({
                    "type": "security_issue",
                    "description": check["description"],
                    "severity": check["severity"],
                    "snippet": code[max(0, match.start() - 20):min(len(code), match.end() + 20)]
                })
                
        return issues
    
    def _check_code_quality(self, code: str) -> List[Dict]:
        """Check code for quality issues"""
        issues = []
        
        quality_checks = [
            {
                "pattern": r"console\.log",
                "description": "Debug statement found",
                "severity": "low"
            },
            {
                "pattern": r"TODO|FIXME",
                "description": "Incomplete code",
                "severity": "medium"
            },
            {
                "pattern": r"function\s+\w+\s*\([^)]{80,}\)",
                "description": "Function with too many parameters",
                "severity": "medium"
            }
        ]
        
        for check in quality_checks:
            for match in re.finditer(check["pattern"], code):
                issues.append({
                    "type": "quality_issue",
                    "description": check["description"],
                    "severity": check["severity"],
                    "snippet": code[max(0, match.start() - 20):min(len(code), match.end() + 20)]
                })
                
        return issues
    
    def _generate_component_task(self, params: Dict) -> Dict:
        """Generate a website component based on specifications"""
        component_type = params.get("type", "")
        component_name = params.get("name", "")
        props = params.get("props", [])
        styling = params.get("styling", {})
        
        if not component_type or not component_name:
            return {"success": False, "error": "Component type and name are required"}
        
        # Generate React component
        try:
            component_code = self._generate_react_component(
                component_name,
                component_type,
                props,
                styling
            )
            
            return {
                "success": True,
                "component": {
                    "name": component_name,
                    "type": component_type,
                    "code": component_code,
                    "checksum": hashlib.md5(component_code.encode()).hexdigest()
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Component generation failed: {str(e)}"}
    
    def _generate_react_component(self, name: str, type_: str, props: List, styling: Dict) -> str:
        """Generate React component code"""
        # Basic component template
        props_list = ", ".join(props) if props else ""
        
        # Extract styling
        color = styling.get("color", "#333")
        bg_color = styling.get("backgroundColor", "#fff")
        padding = styling.get("padding", "1rem")
        
        if type_ == "functional":
            return f"""import React from 'react';

const {name} = ({props_list}) => {{
  const styles = {{
    container: {{
      color: '{color}',
      backgroundColor: '{bg_color}',
      padding: '{padding}',
    }}
  }};

  return (
    <div style={{styles.container}}>
      <h2>{name} Component</h2>
      {/* Component content goes here */}
    </div>
  );
}};

export default {name};
"""
        elif type_ == "class":
            return f"""import React, {{ Component }} from 'react';

class {name} extends Component {{
  constructor(props) {{
    super(props);
    this.state = {{
      // Initial state
    }};
  }}
  
  render() {{
    const styles = {{
      container: {{
        color: '{color}',
        backgroundColor: '{bg_color}',
        padding: '{padding}',
      }}
    }};

    return (
      <div style={{styles.container}}>
        <h2>{name} Component</h2>
        {/* Component content goes here */}
      </div>
    );
  }}
}}

export default {name};
"""
        else:
            raise ValueError(f"Unknown component type: {type_}")
    
    def _execute_tool_task(self, params: Dict) -> Dict:
        """Execute a registered tool"""
        tool_name = params.get("tool", "")
        tool_params = params.get("params", {})
        
        if not tool_name:
            return {"success": False, "error": "Tool name is required"}
            
        if tool_name not in self.tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
            
        try:
            result = self.tools[tool_name](tool_params)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"Tool execution failed: {str(e)}"}
    
    def _handle_llm_request(self, params: Dict) -> Dict:
        """Handle request that needs to be forwarded to an LLM"""
        if not self.api_manager:
            return {"success": False, "error": "API Manager not available"}
            
        context = params.get("context", "default")
        request_data = params.get("data", {})
        
        try:
            result = self.api_manager.perform_request(context, request_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": f"LLM request failed: {str(e)}"}
    
    def _fetch_knowledge(self, params: Dict) -> Dict:
        """Tool to fetch information from agent memory"""
        key = params.get("key", "")
        if not key:
            return {"error": "No key provided"}
            
        value = self.memory.get(key, None)
        return {"key": key, "value": value}
    
    def _store_knowledge(self, params: Dict) -> Dict:
        """Tool to store information in agent memory"""
        key = params.get("key", "")
        value = params.get("value", None)
        
        if not key:
            return {"error": "No key provided"}
            
        self.memory[key] = value
        return {"success": True, "key": key}
    
    def _analyze_text(self, params: Dict) -> Dict:
        """Tool to perform text analysis"""
        text = params.get("text", "")
        if not text:
            return {"error": "No text provided"}
            
        word_count = len(text.split())
        char_count = len(text)
        
        return {
            "word_count": word_count,
            "char_count": char_count,
            "summary": f"Text contains {word_count} words and {char_count} characters"
        }
    
    def _validate_task_input(self, params: Dict) -> bool:
        """Validate task parameters for security issues"""
        # Convert parameters to JSON string for regex checking
        params_str = json.dumps(params)
        
        # Check for sensitive patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, params_str):
                logger.warning(f"Security violation detected in task input")
                return False
                
        return True
    
    def _sanitize_output(self, data: Dict) -> Dict:
        """Sanitize output to remove any sensitive information"""
        # Convert to string for regex replacement
        data_str = json.dumps(data)
        
        # Replace sensitive patterns with [REDACTED]
        for pattern in self.sensitive_patterns:
            data_str = re.sub(pattern, r'\1[REDACTED]\2', data_str)
            
        # Convert back to dictionary
        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            logger.error("Failed to sanitize output")
            return {"success": False, "error": "Output sanitization failed"}
    
    def plan_task_sequence(self, goal: str) -> List[Dict]:
        """
        Create a sequence of tasks to achieve a goal
        
        Args:
            goal: Description of the goal to achieve
            
        Returns:
            List of task dictionaries representing the plan
        """
        # In a production system, this would use LLM-based planning
        # For this example, we'll just create a simple plan
        
        if "website" in goal.lower():
            return [
                {
                    "id": f"task-{uuid.uuid4()}",
                    "type": "generate_component",
                    "params": {
                        "type": "functional",
                        "name": "Header",
                        "props": ["title", "links"],
                        "styling": {"color": "#333", "backgroundColor": "#f5f5f5"}
                    }
                },
                {
                    "id": f"task-{uuid.uuid4()}",
                    "type": "generate_component",
                    "params": {
                        "type": "functional",
                        "name": "Footer",
                        "props": ["copyright"],
                        "styling": {"color": "#333", "backgroundColor": "#f5f5f5"}
                    }
                },
                {
                    "id": f"task-{uuid.uuid4()}",
                    "type": "generate_component",
                    "params": {
                        "type": "functional",
                        "name": "MainContent",
                        "props": ["content"],
                        "styling": {"color": "#333", "backgroundColor": "#fff"}
                    }
                }
            ]
        elif "analyze" in goal.lower():
            return [
                {
                    "id": f"task-{uuid.uuid4()}",
                    "type": "process_text",
                    "params": {
                        "text": goal,
                        "analysis_type": "summarization"
                    }
                }
            ]
        else:
            return [
                {
                    "id": f"task-{uuid.uuid4()}",
                    "type": "llm_request",
                    "params": {
                        "context": "chat",
                        "data": {
                            "query": goal
                        }
                    }
                }
            ]
    
    def execute_plan(self, tasks: List[Dict]) -> List[Dict]:
        """
        Execute a sequence of tasks according to a plan
        
        Args:
            tasks: List of task dictionaries to execute
            
        Returns:
            List of result dictionaries
        """
        results = []
        for task in tasks:
            result = self.execute_task(task)
            results.append(result)
            
            # If a task fails, stop execution
            if not result.get("success", False):
                break
                
        return results
    
    def save_state(self) -> bool:
        """Save agent state to disk"""
        if not self.config.get("memory_path"):
            logger.warning("No memory path configured, state not saved")
            return False
            
        try:
            memory_path = self.config.get("memory_path")
            os.makedirs(os.path.dirname(memory_path), exist_ok=True)
            
            with open(memory_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
                
            logger.info(f"Agent state saved to {memory_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save agent state: {str(e)}")
            return False
    
    def log(self, message: str, level: str = "info") -> None:
        """Add an entry to the agent's log"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": level
        }
        self.logs.append(entry)
        
        # Also log to the Python logger
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)


class ChatAgent(Agent):
    """Specialized agent for chat interactions"""
    
    def __init__(self, config: Dict = None, agent_id: str = None):
        super().__init__(config, agent_id or "chat-agent")
        self.conversation_history = []
        
        # Register chat-specific tools
        self.register_tool("retrieve_chat_history", self._retrieve_chat_history)
    
    def process_message(self, user_message: str) -> Dict:
        """Process a user message and generate a response"""
        # Add message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create a task for the message
        task = {
            "id": f"msg-{uuid.uuid4()}",
            "type": "llm_request",
            "params": {
                "context": "chat",
                "data": {
                    "message": user_message,
                    "history": self.conversation_history[-5:]  # Last 5 messages for context
                }
            }
        }
        
        # Execute the task
        result = self.execute_task(task)
        
        if result.get("success", False):
            # Add response to conversation history
            response = result.get("result", {}).get("response", "I don't know how to respond to that.")
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            return {"response": response, "success": True}
        else:
            error_msg = "Sorry, I encountered an error processing your message."
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": datetime.now().isoformat()
            })
            return {"response": error_msg, "success": False, "error": result.get("error")}
    
    def _retrieve_chat_history(self, params: Dict) -> Dict:
        """Tool to retrieve chat history"""
        limit = params.get("limit", 10)
        return {"history": self.conversation_history[-limit:] if limit > 0 else self.conversation_history}


class DeveloperAgent(Agent):
    """Specialized agent for software development tasks"""
    
    def __init__(self, config: Dict = None, agent_id: str = None):
        super().__init__(config, agent_id or "dev-agent")
        self.codebase_knowledge = {}
        
        # Register developer-specific tools
        self.register_tool("analyze_repository", self._analyze_repository)
        self.register_tool("generate_component", self._generate_component)
        self.register_tool("refactor_code", self._refactor_code)
    
    def _analyze_repository(self, params: Dict) -> Dict:
        """Tool to analyze a code repository"""
        repo_path = params.get("path", ".")
        if not os.path.exists(repo_path):
            return {"error": f"Repository path not found: {repo_path}"}
            
        file_count = sum(len(files) for _, _, files in os.walk(repo_path))
        
        return {
            "files": file_count,
            "summary": f"Repository contains {file_count} files"
        }
    
    def _generate_component(self, params: Dict) -> Dict:
        """Tool to generate a software component"""
        return self._generate_component_task(params)
    
    def _refactor_code(self, params: Dict) -> Dict:
        """Tool to refactor code"""
        code = params.get("code", "")
        refactor_type = params.get("refactor_type", "")
        
        if not code:
            return {"error": "No code provided"}
            
        # Very basic refactoring example
        if refactor_type == "cleanup":
            # Remove console.log statements
            refactored = re.sub(r'console\.log\([^)]*\);?', '', code)
            return {"refactored_code": refactored}
        else:
            return {"error": f"Unsupported refactor type: {refactor_type}"}
    
    def design_website_structure(self, params: Dict) -> Dict:
        """Design the structure of a website"""
        try:
            # This would typically use an LLM for more sophisticated designs
            components = ["Header", "Footer", "MainContent", "Sidebar", "Navigation"]
            pages = ["Home", "About", "Contact", "Services", "Blog"]
            
            architecture = {
                "components": {
                    "layout": [
                        {"name": "Header", "reusable": True},
                        {"name": "Footer", "reusable": True},
                        {"name": "Sidebar", "reusable": True}
                    ],
                    "ui": [
                        {"name": "Button", "variants": ["Primary", "Secondary", "Text"]},
                        {"name": "Card", "variants": ["Default", "Highlighted"]},
                        {"name": "Input", "variants": ["Text", "Select", "Checkbox"]}
                    ]
                },
                "pages": [
                    {"name": page, "path": page.lower() if page != "Home" else "/"} for page in pages
                ],
                "styling": {
                    "colors": {
                        "primary": "#3498db",
                        "secondary": "#2ecc71",
                        "text": "#333333",
                        "background": "#ffffff"
                    },
                    "typography": {
                        "fontFamily": "Inter, system-ui, sans-serif",
                    }
                }
            }
            
            return {"success": True, "architecture": architecture}
        except Exception as e:
            return {"success": False, "error": f"Website design failed: {str(e)}"}


# Helper factory function to create the appropriate agent type
def create_agent(agent_type: str, config: Dict = None) -> Agent:
    """Create and return an agent of the specified type"""
    if agent_type == "chat":
        return ChatAgent(config)
    elif agent_type == "developer":
        return DeveloperAgent(config)
    else:
        return Agent(config)
