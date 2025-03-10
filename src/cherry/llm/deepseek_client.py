import os
import re
import logging
import httpx
from typing import Dict, List, Any, Optional

logger = logging.getLogger("cherry.llm.deepseek")


class DeepSeekClient:
    """
    Client for interacting with the DeepSeek-V3 API
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the DeepSeek client.

        Args:
            api_key: API key for DeepSeek. If None, will attempt to read from DEEPSEEK_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.api_url = os.environ.get(
            "DEEPSEEK_API_URL", "https://api.deepseek.ai/v3/chat/completions")

        if not self.api_key:
            logger.warning(
                "No DeepSeek API key provided. Set DEEPSEEK_API_KEY environment variable.")

    async def _call_api(self, messages: List[Dict[str, str]],
                        temperature: float = 0.7,
                        max_tokens: int = 4000,
                        retries: int = 3) -> Dict:
        """
        Make an API call to DeepSeek-V3.

        Args:
            messages: List of message objects with role and content
            temperature: Controls randomness (lower = more deterministic)
            max_tokens: Maximum tokens to generate
            retries: Number of retries on failure

        Returns:
            The API response as a dictionary

        Raises:
            Exception: If the API call fails after retries
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-v3",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        attempt = 0
        last_error = None

        while attempt < retries:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.api_url,
                        json=payload,
                        headers=headers,
                        timeout=90.0  # Increased timeout for complex generations
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as e:
                last_error = e
                attempt += 1
                logger.warning(
                    f"DeepSeek API call failed (attempt {attempt}/{retries}): {str(e)}")
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        # If we reach here, all retries failed
        logger.error(
            f"DeepSeek API call failed after {retries} attempts: {last_error}")
        raise last_error

    async def generate_code(self, context):
        """
        Generate code based on the provided context.

        Args:
            context: CodeContext object containing requirements and other information

        Returns:
            CodeSolution object containing the generated code and metadata
        """
        from cherry.coding.agent_system import CodeSolution

        # Format context files for the prompt
        context_files_text = ""
        if hasattr(context, 'context_files') and context.context_files:
            for path, content in context.context_files.items():
                context_files_text += f"\nFILE: {path}\n```\n{content}\n```\n"

        # Build an enhanced prompt
        prompt = f"""Generate {context.language} code for the file {context.file_path}.

Project: {context.project_name}

Requirements:
{context.requirements}

{context_files_text}

Please provide production-ready code following best practices for {context.language}.
Include proper error handling, input validation, and comments.
The code should be efficient, maintainable, and secure.
"""

        messages = [
            {"role": "system", "content": "You are an expert software developer specializing in writing high-quality, production-ready code."},
            {"role": "user", "content": prompt}
        ]

        try:
            # Call the API with lower temperature for code generation
            result = await self._call_api(messages, temperature=0.2)
            response_content = result["choices"][0]["message"]["content"]

            # Extract code from markdown code blocks if present
            code = self._extract_code_from_markdown(
                response_content, context.language)

            # Get an explanation in a separate call for better results
            explanation = await self._get_explanation(code, context)

            # Create and return the solution
            return CodeSolution(
                agent_name="deepseek_v3",
                code=code,
                explanation=explanation,
                confidence=0.9,
                metadata={
                    "model": "deepseek-v3",
                    "temperature": 0.2
                }
            )
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise

    async def _get_explanation(self, code: str, context) -> str:
        """Get an explanation of the generated code"""
        explanation_prompt = f"""Explain the following {context.language} code:

```{context.language}
{code}
```
"""
        messages = [
            {"role": "system", "content": "You are an expert code reviewer who provides thorough, actionable feedback."},
            {"role": "user", "content": prompt}
        ]

        try:
            result = await self._call_api(messages)
            review_text = result["choices"][0]["message"]["content"]

            # Parse the review
            is_valid = self._extract_validity(review_text)
            score = self._extract_score(review_text)
            issues = self._extract_issues(review_text)
            suggestions = self._extract_suggestions(review_text)

            # Import locally to avoid circular imports
            from cherry.coding.agent_system import ValidationResult, CodeReviewStage

            # Convert string stage to enum
            stage_map = {
                "general": CodeReviewStage.INITIAL_GENERATION,
                "security": CodeReviewStage.SECURITY_REVIEW,
                "performance": CodeReviewStage.PERFORMANCE_REVIEW,
                "testing": CodeReviewStage.DYNAMIC_TESTING
            }

            review_stage_enum = stage_map.get(
                review_stage, CodeReviewStage.INITIAL_GENERATION)

            return ValidationResult(
                stage=review_stage_enum,
                agent_name="deepseek_v3",
                is_valid=is_valid,
                score=score,
                issues=issues,
                suggestions=suggestions,
                metadata={"full_review": review_text}
            )
        except Exception as e:
            logger.error(f"Error reviewing code: {str(e)}")
            raise

    async def improve_code(self, code: str, context, issues: List[Dict], suggestions: List[Dict]) -> str:
        """
        Improve code based on review feedback.

        Args:
            code: Original code
            context: CodeContext containing requirements
            issues: List of issues to fix
            suggestions: List of suggestions to implement

        Returns:
            Improved code as a string
        """
        # Format issues and suggestions
        issues_text = "\n".join(
            [f"- {issue['description']}" for issue in issues]) if issues else "None identified."
        suggestions_text = "\n".join(
            [f"- {suggestion['description']}" for suggestion in suggestions]) if suggestions else "None provided."

        prompt = f"""Improve the following {context.language} code:
```
{code}
```
Issues:
{issues_text}

Suggestions:
{suggestions_text}

Provide the improved code.
"""
        messages = [
            {"role": "system", "content": "You are an expert software developer focusing on improving existing code."},
            {"role": "user", "content": prompt}
        ]

        try:
            result = await self._call_api(messages, temperature=0.2)
            response_content = result["choices"][0]["message"]["content"]

            # Extract code from markdown code blocks if present
            return self._extract_code_from_markdown(response_content, context.language)
        except Exception as e:
            logger.error(f"Error improving code: {str(e)}")
            raise

    def _extract_code_from_markdown(self, text: str, language: str = None) -> str:
        """Extract code from markdown code blocks"""
        # Look for code blocks with or without language specification
        pattern = r"```(?:\w+)?\s*(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()
        return text.strip()

    def _extract_validity(self, review_text: str) -> bool:
        """Extract validity assessment from review text"""
        validity_patterns = [
            r"(?:is|the code is).*?\b(valid|correct)\b.*?\b(yes|no)\b",
            r"\b(yes|no)\b.*?(?:the code is|is).*?\b(valid|correct)\b"
        ]

        for pattern in validity_patterns:
            match = re.search(pattern, review_text, re.IGNORECASE)
            if match and any('yes' in g.lower() for g in match.groups()):
                return True

        return False

    def _extract_score(self, review_text: str) -> float:
        """Extract numeric score from review text"""
        score_match = re.search(
            r'(?:score|quality)[^\d]*?(\d+)', review_text, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            return min(100, max(0, score)) / 100  # Normalize to 0-1
        return 0.5  # Default middle score

    def _extract_issues(self, review_text: str) -> List[Dict]:
        """Extract issues from review text"""
        # Find issues section
        issues_section = re.search(
            r'(?:issues|problems)[^\n]*?:(.+?)(?=(?:suggestions|improvements|explanation|$))',
            review_text,
            re.IGNORECASE | re.DOTALL
        )

        issues = []
        if issues_section:
            # Find bullet points or numbered items
            items = re.findall(
                r'(?:^|\n)[\s*\-\d.]+([^\n]+)', issues_section.group(1))
            issues = [{"description": item.strip()}
                      for item in items if item.strip()]

        return issues

    def _extract_suggestions(self, review_text: str) -> List[Dict]:
        """Extract suggestions from review text"""
        # Find suggestions section
        suggestions_section = re.search(
            r'(?:suggestions|improvements)[^\n]*?:(.+?)(?=(?:issues|problems|explanation|$))',
            review_text,
            re.IGNORECASE | re.DOTALL
        )

        suggestions = []
        if suggestions_section:
            # Find bullet points or numbered items
            items = re.findall(
                r'(?:^|\n)[\s*\-\d.]+([^\n]+)', suggestions_section.group(1))
            suggestions = [{"description": item.strip()}
                           for item in items if item.strip()]

        return suggestions
