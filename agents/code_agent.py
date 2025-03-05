from typing import Dict, Any, List, Optional
import re
from agents.base import Agent

class CodeAgent(Agent):
    """
    Agent specialized in code generation, analysis, and troubleshooting
    based on natural language requests.
    """
    
    def __init__(self, config: Dict[str, Any], llm=None):
        super().__init__(config, llm)
        self.name = "code_agent"
        self.description = "Generates, analyzes, and troubleshoots programming code"
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "c", "c++", "c#",
            "go", "rust", "ruby", "php", "swift", "kotlin", "bash", "sql", "r"
        ]

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a code-related query and return the appropriate response."""
        if not context:
            context = {}
        
        # Determine the type of code task
        task_type = self._determine_task_type(query)
        
        # Process according to task type
        if task_type == "generate":
            return await self._generate_code(query, context)
        elif task_type == "analyze":
            return await self._analyze_code(query, context)
        elif task_type == "troubleshoot":
            return await self._troubleshoot_code(query, context)
        else:
            # General code assistance
            return await self._general_code_help(query, context)
    
    def _determine_task_type(self, query: str) -> str:
        """Determine the type of code task from the query."""
        query_lower = query.lower()
        
        # Check for generation keywords
        if any(kw in query_lower for kw in ["create", "generate", "write", "implement", "build"]):
            return "generate"
            
        # Check for analysis keywords
        if any(kw in query_lower for kw in ["analyze", "explain", "understand", "review", "assess"]):
            return "analyze"
            
        # Check for troubleshooting keywords
        if any(kw in query_lower for kw in ["fix", "debug", "troubleshoot", "solve", "error", "issue", "problem"]):
            return "troubleshoot"
            
        # Default to general help
        return "general"
    
    async def _generate_code(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on the query."""
        language = self._extract_language(query, context)
        task_description = self._clean_query(query)
        
        prompt = f"""
        Generate {language} code that accomplishes the following:
        {task_description}
        
        Provide detailed comments explaining how the code works.
        """
        
        response = await self.llm_call(prompt)
        code_blocks = self._extract_code_blocks(response)
        
        return {
            "type": "code_generation",
            "language": language,
            "task": task_description,
            "code": code_blocks,
            "explanation": self._extract_explanation(response, code_blocks)
        }
    
    async def _analyze_code(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and explain code."""
        code_to_analyze = self._extract_code_from_context(context)
        
        if not code_to_analyze:
            return {
                "type": "error",
                "message": "No code found to analyze. Please provide code in your query."
            }
        
        prompt = f"""
        Analyze the following code:
        
        {code_to_analyze}
        
        Explain what the code does, its structure, potential improvements, 
        and any issues or inefficiencies you notice.
        """
        
        response = await self.llm_call(prompt)
        
        return {
            "type": "code_analysis",
            "code": code_to_analyze,
            "analysis": response
        }
    
    async def _troubleshoot_code(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Troubleshoot code problems."""
        code_to_troubleshoot = self._extract_code_from_context(context)
        error_message = self._extract_error_message(query, context)
        
        if not code_to_troubleshoot:
            return {
                "type": "error",
                "message": "No code found to troubleshoot. Please provide your code."
            }
        
        prompt = f"""
        Troubleshoot the following code:
        
        {code_to_troubleshoot}
        
        {"Error message: " + error_message if error_message else "Identify potential issues in this code."}
        
        Provide a detailed explanation of the problem and a corrected version of the code.
        """
        
        response = await self.llm_call(prompt)
        fixed_code = self._extract_code_blocks(response)
        
        return {
            "type": "code_troubleshooting",
            "original_code": code_to_troubleshoot,
            "error": error_message,
            "fixed_code": fixed_code,
            "explanation": self._extract_explanation(response, fixed_code)
        }
    
    async def _general_code_help(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general code-related assistance."""
        prompt = f"""
        Assist with the following code-related query:
        {query}
        """
        
        response = await self.llm_call(prompt)
        code_blocks = self._extract_code_blocks(response)
        
        return {
            "type": "code_assistance",
            "query": query,
            "response": response,
            "code_examples": code_blocks
        }
    
    def _extract_language(self, query: str, context: Dict[str, Any]) -> str:
        """Extract programming language from query or context."""
        # Check context first
        if context.get("language"):
            return context["language"]
        
        # Try to extract from query
        query_lower = query.lower()
        for lang in self.supported_languages:
            if lang in query_lower:
                return lang
        
        # Default to Python if nothing found
        return "python"
    
    def _clean_query(self, query: str) -> str:
        """Clean query by removing language specification instructions."""
        # Remove phrases like "in Python" or "using JavaScript"
        for lang in self.supported_languages:
            query = re.sub(f"\\b(in|using|with|for) {lang}\\b", "", query, flags=re.IGNORECASE)
        
        return query.strip()
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text."""
        # Look for code blocks wrapped in ```
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks
        
        # If no ``` blocks, look for indented code blocks
        lines = text.split("\n")
        code_blocks = []
        current_block = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith("    ") and not in_code_block:
                in_code_block = True
                current_block.append(line.strip())
            elif line.strip().startswith("    ") and in_code_block:
                current_block.append(line.strip())
            elif not line.strip().startswith("    ") and in_code_block:
                in_code_block = False
                if current_block:
                    code_blocks.append("\n".join(current_block))
                    current_block = []
        
        # Don't forget the last block
        if current_block:
            code_blocks.append("\n".join(current_block))
        
        return code_blocks
    
    def _extract_code_from_context(self, context: Dict[str, Any]) -> str:
        """Extract code from context."""
        if context.get("code"):
            return context["code"]
        
        if context.get("messages"):
            # Look for code in previous messages
            for msg in reversed(context["messages"]):
                code_blocks = self._extract_code_blocks(msg.get("content", ""))
                if code_blocks:
                    return code_blocks[0]
        
        return ""
    
    def _extract_error_message(self, query: str, context: Dict[str, Any]) -> str:
        """Extract error message from query or context."""
        if context.get("error"):
            return context["error"]
        
        # Look for error patterns in query
        error_patterns = [
            r"Error: (.*?)(?:\n|$)",
            r"Exception: (.*?)(?:\n|$)",
            r"traceback[:\s]+(.*?)(?:\n\n|\n$|$)",
            r"error[:\s]+(.*?)(?:\n\n|\n$|$)"
        ]
        
        for pattern in error_patterns:
            matches = re.search(pattern, query, re.IGNORECASE | re.DOTALL)
            if matches:
                return matches.group(1).strip()
        
        return ""
    
    def _extract_explanation(self, response: str, code_blocks: List[str]) -> str:
        """Extract explanation part from the response."""
        # Remove code blocks from response to get explanation
        explanation = response
        for block in code_blocks:
            explanation = explanation.replace(f"```\n{block}\n```", "")
            explanation = explanation.replace(f"```python\n{block}\n```", "")
        
        return explanation.strip()
