import os
import logging
from typing import Dict, Any, List, Optional
import openai
from cherry.agents.base_agent import Agent
from cherry.agents.planning_agent import PlanningAgent

logger = logging.getLogger(__name__)


class LanguageAgent(Agent):
    """
    Agent that processes natural language requests from users and routes them
    to appropriate specialized agents or handles them directly.

    This agent serves as the main interface between the user and Cherry's capabilities.
    """

    def __init__(self, name: str = "Language Agent", description: str = "Processes natural language requests"):
        super().__init__(name, description)
        self.capabilities = [
            "natural language understanding",
            "intent classification",
            "request routing",
            "response generation"
        ]
        # Store registered agents that can handle different types of tasks
        self._registered_agents = {}
        self._conversation_history = []

    def register_agent(self, task_type: str, agent: Agent) -> None:
        """Register an agent to handle a specific task type."""
        self._registered_agents[task_type] = agent
        logger.info(f"Registered agent for task type: {task_type}")

    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a natural language request.

        Args:
            task_data: Dictionary containing:
                - user_input: The natural language input from the user
                - session_id: Optional session identifier for maintaining context

        Returns:
            Dictionary containing the response and any relevant data
        """
        user_input = task_data.get('user_input', '')
        session_id = task_data.get('session_id', 'default')

        if not user_input:
            return {"error": "No user input provided"}

        # Store the user input in conversation history
        self._conversation_history.append(
            {"role": "user", "content": user_input})

        try:
            # Classify the intent of the user's request
            intent_data = await self._classify_intent(user_input)
            intent_type = intent_data.get("intent_type", "general")

            # Route to appropriate agent based on intent
            if intent_type in self._registered_agents:
                agent = self._registered_agents[intent_type]
                agent_task_data = {
                    "original_input": user_input,
                    **intent_data
                }
                result = await agent.process(agent_task_data)
                response = result.get(
                    "response", "Task completed successfully")
            else:
                # Handle general requests directly
                response = await self._generate_general_response(user_input)
                result = {"response": response}

            # Store the system response in conversation history
            self._conversation_history.append(
                {"role": "system", "content": response})

            return {
                "response": response,
                "intent": intent_type,
                "session_id": session_id,
                "details": result
            }

        except Exception as e:
            logger.error(f"Error processing language request: {e}")
            return {"error": str(e), "response": "Sorry, I encountered an error processing your request."}

    async def _classify_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Classify the intent of the user's input to determine how to route it.

        Returns a dictionary with intent classification details.
        """
        try:
            # Use OpenAI to classify the intent
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
                    Classify the user's intent into one of the following categories:
                    - planning: Requests related to planning, task breakdown, estimation
                    - coding: Requests for code generation or modification
                    - explanation: Requests for explanations or information
                    - general: General conversation or other requests
                    
                    Return a JSON object with the format:
                    {"intent_type": "category", "details": {relevant details based on intent}}
                    """},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                max_tokens=150
            )

            result = response.choices[0].message.content.strip()
            # Basic parsing - in a real system, use proper JSON parsing
            if "planning" in result.lower():
                return {"intent_type": "planning", "task_type": "breakdown", "requirements": [user_input]}
            elif "coding" in result.lower():
                return {"intent_type": "coding", "request": user_input}
            elif "explanation" in result.lower():
                return {"intent_type": "explanation", "query": user_input}
            else:
                return {"intent_type": "general"}

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return {"intent_type": "general"}

    async def _generate_general_response(self, user_input: str) -> str:
        """Generate a response for general conversation."""
        try:
            conversation = [
                {"role": "system", "content": "You are Cherry, an AI coding assistant."}]
            # Add the last few exchanges for context
            history_limit = min(5, len(self._conversation_history))
            conversation.extend(self._conversation_history[-history_limit:])

            # Add the current user input
            conversation.append({"role": "user", "content": user_input})

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=conversation,
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble generating a response right now."

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._conversation_history = []
