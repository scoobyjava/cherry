import os
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
import openai

logger = logging.getLogger(__name__)


class CopilotIntegration:
    """
    Integration with GitHub Copilot for getting code deployment and best practice advice.

    This class simulates GitHub Copilot integration by using OpenAI APIs with prompts
    that focus on deployment strategies and best practices.
    """

    def __init__(self):
        """Initialize the Copilot integration."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY not set, Copilot integration will have limited functionality")

    async def get_deployment_advice(self, code_proposal: Dict[str, Any]) -> str:
        """
        Get deployment advice from GitHub Copilot based on a code proposal.

        Args:
            code_proposal: Dictionary containing:
                - description: Description of the code
                - files: List of files with their content
                - type: Type of proposal (new_code or modification)

        Returns:
            String with deployment advice
        """
        if not code_proposal or "files" not in code_proposal:
            return "No valid code proposal provided for deployment advice."

        # Create a summary of the files for the prompt
        files_summary = ""
        for file in code_proposal.get("files", []):
            path = file.get("path", "unknown")
            content = file.get("content", "")
            # Limit content length for the prompt
            content_preview = content[:500] + \
                "..." if len(content) > 500 else content
            files_summary += f"\n\nFile: {path}\n```\n{content_preview}\n```"

        prompt = f"""
        # Request for Deployment Advice
        
        I need advice on the best way to deploy the following code changes:
        
        ## Code Description:
        {code_proposal.get('description', 'No description provided')}
        
        ## Code Type:
        {code_proposal.get('type', 'unknown')}
        
        ## Files:
        {files_summary}
        
        ## Questions:
        1. What's the best way to deploy these changes?
        2. Are there any potential issues or considerations before deployment?
        3. What testing should be done before deployment?
        4. Are there any performance optimizations that should be considered?
        5. What monitoring or observability should be set up post-deployment?
        
        Please provide practical advice that considers best practices for software deployment.
        """

        try:
            # This simulates GitHub Copilot by using OpenAI's API
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are GitHub Copilot, an AI assistant that provides expert advice on code deployment and best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )

            advice = response.choices[0].message.content.strip()
            return advice

        except Exception as e:
            logger.error(f"Error getting deployment advice from Copilot: {e}")
            return f"Sorry, I encountered an error while getting deployment advice: {str(e)}"

    async def check_best_practices(self, code_content: str, language: str) -> Dict[str, Any]:
        """
        Check code against best practices using GitHub Copilot.

        Args:
            code_content: The code content to check
            language: The programming language

        Returns:
            Dictionary with best practice suggestions
        """
        prompt = f"""
        # Code Review for Best Practices
        
        Please review this {language} code and provide feedback on best practices:
        
        ```{language}
        {code_content}
        ```
        
        Focus on:
        - Code quality
        - Performance
        - Security
        - Maintainability
        - Testing considerations
        
        Format your response as a JSON object with the following structure:
        {{
            "overall_rating": 1-10,
            "strengths": ["strength1", "strength2", ...],
            "improvement_areas": [
                {{
                    "issue": "Description of issue",
                    "suggestion": "Suggestion to improve",
                    "severity": "high/medium/low"
                }},
                ...
            ],
            "summary": "Overall feedback summary"
        }}
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are GitHub Copilot, an AI assistant that provides expert code reviews and best practice recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            result = response.choices[0].message.content.strip()

            # Try to parse JSON from the response
            try:
                # Extract JSON if it's wrapped in code blocks
                import re
                json_match = re.search(
                    r'```(?:json)?\s*(\{.*?\})\s*```', result, re.DOTALL)
                if json_match:
                    result = json_match.group(1)

                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning(
                    "Failed to parse JSON response from best practices check")
                return {
                    "overall_rating": 5,
                    "summary": "Could not parse structured feedback. Here's the raw feedback:\n\n" + result
                }

        except Exception as e:
            logger.error(f"Error checking best practices: {e}")
            return {
                "error": str(e),
                "overall_rating": 0,
                "summary": "An error occurred while checking best practices."
            }
