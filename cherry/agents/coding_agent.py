import os
import logging
import json
import re
from typing import Dict, Any, List, Optional
import openai

from cherry.agents.base_agent import Agent

logger = logging.getLogger(__name__)


class CodingAgent(Agent):
    """
    Agent responsible for generating and modifying code based on natural language requests.

    This agent can:
    - Generate new code based on requirements
    - Propose modifications to existing code
    - Analyze code for improvements
    - Handle different programming languages
    """

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.capabilities = [
            "code generation",
            "code modification",
            "bug fixing",
            "code analysis",
            "refactoring suggestions"
        ]
        self._supported_languages = [
            "python", "javascript", "typescript", "java", "c#",
            "c++", "go", "rust", "ruby", "php", "html", "css"
        ]

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a coding-related task.

        Args:
            task_data: Dictionary containing:
                - request: The natural language request
                - language: Optional preferred programming language
                - files: Optional list of files to modify
                - context: Optional additional context

        Returns:
            Dictionary containing the response and any relevant data
        """
        logger.info(
            f"Processing coding task: {task_data.get('request', '')[:100]}...")

        try:
            request = task_data.get('request', '')
            language = task_data.get('language', 'python')
            files = task_data.get('files', [])
            context = task_data.get('context', '')

            if not request:
                return {"error": "No coding request provided"}

            # Determine the task type
            if self._is_code_modification_request(request):
                if not files:
                    return {
                        "response": "I'd like to help modify code, but no files were provided. Could you specify which files need to be modified?",
                        "needs_files": True
                    }
                proposal = await self._generate_code_modification(request, files, language, context)
            else:
                proposal = await self._generate_new_code(request, language, context)

            response = self._create_human_readable_response(proposal)

            return {
                "response": response,
                "code_proposal": proposal
            }

        except Exception as e:
            logger.error(f"Error in coding agent: {e}")
            return {"error": str(e)}

    def _is_code_modification_request(self, request: str) -> bool:
        """Determine if the request is for modifying existing code."""
        modify_keywords = ['change', 'update', 'modify',
                           'fix', 'refactor', 'improve', 'edit']
        return any(keyword in request.lower() for keyword in modify_keywords)

    async def _generate_new_code(self, request: str, language: str, context: str) -> Dict[str, Any]:
        """Generate new code based on the user's request."""
        prompt = f"""
        # Request for New Code
        
        Generate code based on the following request:
        "{request}"
        
        ## Requirements:
        - Use {language} as the programming language
        - Include proper documentation and comments
        - Follow best practices for {language}
        
        ## Additional Context:
        {context}
        
        ## Output Format:
        Generate executable code that fulfills the request. Create appropriate file structures.
        For each file, provide:
        1. A suggested file path
        2. The complete code content
        
        Format your response as a JSON object with the following structure:
        {{
            "description": "Brief description of what the code does",
            "files": [
                {{
                    "path": "suggested/file/path.ext",
                    "content": "The complete code"
                }},
                ...
            ]
        }}
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Generate code that is clean, efficient, and follows best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )

            result = response.choices[0].message.content.strip()

            # Extract JSON content from the response
            json_match = re.search(
                r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})', result)
            if json_match:
                json_content = json_match.group(1) or json_match.group(2)
                try:
                    proposal = json.loads(json_content)
                    return {
                        "type": "new_code",
                        "description": proposal.get("description", "New code generated"),
                        "files": proposal.get("files", []),
                        "code": result
                    }
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse JSON response, returning raw text")

            # Fallback to handle case when properly formatted JSON isn't returned
            return {
                "type": "new_code",
                "description": "New code generated",
                "files": [{"path": f"new_code.{language}", "content": result}],
                "code": result
            }

        except Exception as e:
            logger.error(f"Error generating new code: {e}")
            return {
                "type": "error",
                "description": f"Error generating code: {str(e)}",
                "files": [],
                "code": ""
            }

    async def _generate_code_modification(self, request: str, files: List[Dict[str, str]],
                                          language: str, context: str) -> Dict[str, Any]:
        """Generate modifications to existing code based on the user's request."""
        file_contents_str = ""
        for idx, file_info in enumerate(files):
            path = file_info.get("path", f"file_{idx}")
            content = file_info.get("content", "")
            file_contents_str += f"\n\nFile: {path}\n```\n{content}\n```"

        prompt = f"""
        # Request for Code Modification
        
        The following request describes changes needed to existing code:
        "{request}"
        
        ## Existing Code:
        {file_contents_str}
        
        ## Additional Context:
        {context}
        
        ## Output Format:
        Modify the existing code to fulfill the request. Provide the complete updated code for each file that needs changes.
        Format your response as a JSON object with the following structure:
        {{
            "description": "Brief description of the changes made",
            "files": [
                {{
                    "path": "file/path.ext",
                    "content": "The complete updated code"
                }},
                ...
            ]
        }}
        
        Only include files that require changes. For each file, provide the complete updated code, not just the changes.
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Modify code to be clean, efficient, and follow best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )

            result = response.choices[0].message.content.strip()

            # Extract JSON content from the response
            json_match = re.search(
                r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})', result)
            if json_match:
                json_content = json_match.group(1) or json_match.group(2)
                try:
                    proposal = json.loads(json_content)
                    return {
                        "type": "modification",
                        "description": proposal.get("description", "Code modifications generated"),
                        "files": proposal.get("files", []),
                        "code": result
                    }
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse JSON response, returning raw text")

            # Fallback to handle case when properly formatted JSON isn't returned
            return {
                "type": "modification",
                "description": "Code modifications generated",
                "files": files,  # Return original files if parsing fails
                "code": result
            }

        except Exception as e:
            logger.error(f"Error generating code modification: {e}")
            return {
                "type": "error",
                "description": f"Error modifying code: {str(e)}",
                "files": [],
                "code": ""
            }

    def _create_human_readable_response(self, proposal: Dict[str, Any]) -> str:
        """Create a human-readable response describing the code proposal."""
        if proposal.get("type") == "error":
            return f"I encountered an error while working on your code: {proposal.get('description', 'Unknown error')}"

        description = proposal.get("description", "")
        num_files = len(proposal.get("files", []))

        if proposal.get("type") == "new_code":
            response = f"I've created {num_files} file(s) based on your request. {description}"
        else:
            response = f"I've modified {num_files} file(s) based on your request. {description}"

        if num_files > 0:
            response += "\n\nHere's a summary of the files:"
            for file in proposal.get("files", []):
                path = file.get("path", "unknown_file")
                content_preview = file.get("content", "")[
                    :50].replace("\n", " ")
                response += f"\n- {path}: {content_preview}..."

        response += "\n\nWould you like to view the full code proposal?"
        return response
