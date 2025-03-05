import asyncio
import argparse
import logging
from typing import Dict, Any, List
import sys
import os
import json
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from cherry.core.orchestrator import Orchestrator
from cherry.agents.planning_agent import PlanningAgent
from cherry.agents.coding_agent import CodingAgent
from cherry.agents.documentation_agent import DocumentationAgent

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Styling for the CLI
cherry_style = Style.from_dict({
    'prompt': 'ansibrightmagenta',
    'user-input': 'ansibrightgreen',
    'cherry-output': 'ansibrightcyan',
    'cherry-error': 'ansibrightyellow',
    'cherry-warning': 'ansibrightyellow',
})


class CherryCLI:
    """Command-line interface for interacting with Cherry."""

    def __init__(self):
        self.orchestrator = Orchestrator()
        self.session = PromptSession(style=cherry_style)
        self.running = False

    async def setup(self):
        """Initialize Cherry and its agents."""
        # Register the core agents
        planning_agent = PlanningAgent(
            name="Planning Agent",
            description="Plans development tasks and creates roadmaps"
        )
        self.orchestrator.register_agent(planning_agent)

        # These agents would need to be implemented
        coding_agent = CodingAgent(
            name="Coding Agent",
            description="Generates and modifies code based on requirements"
        )
        self.orchestrator.register_agent(coding_agent)

        documentation_agent = DocumentationAgent(
            name="Documentation Agent",
            description="Creates documentation and explains code"
        )
        self.orchestrator.register_agent(documentation_agent)

        # Start the orchestrator
        await self.orchestrator.start()
        logger.info("Cherry CLI initialized successfully")

    async def start_interactive(self):
        """Start the interactive CLI session."""
        self.running = True

        # Print welcome message
        print(HTML("<cherry-output>\n" +
                   "🍒 Cherry AI Assistant\n" +
                   "Type 'help' for available commands or use natural language to ask Cherry to perform tasks.\n" +
                   "Type 'exit' to quit.\n" +
                   "</cherry-output>"))

        while self.running:
            try:
                # Get user input
                user_input = await self.session.prompt_async(HTML('<prompt>Cherry> </prompt>'), style=cherry_style)

                # Process special commands
                if user_input.lower() == 'exit':
                    self.running = False
                    continue
                elif user_input.lower() == 'help':
                    await self._show_help()
                    continue
                elif user_input.lower() == 'status':
                    await self._show_status()
                    continue
                elif user_input.lower().startswith('approve '):
                    _, task_id = user_input.split(' ', 1)
                    await self._approve_task(task_id, True)
                    continue
                elif user_input.lower().startswith('reject '):
                    _, task_id = user_input.split(' ', 1)
                    await self._approve_task(task_id, False)
                    continue

                # Process as natural language request
                await self._process_natural_language(user_input)

            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(HTML(f"<cherry-error>Error: {e}</cherry-error>"))
                logger.error(f"CLI error: {e}")

        # Clean shutdown
        await self.orchestrator.stop()
        print(HTML("<cherry-output>Cherry has been shut down. Goodbye!</cherry-output>"))

    async def _show_help(self):
        """Show available commands."""
        help_text = """
        <cherry-output>
        Available commands:
        - help: Show this help message
        - status: Show current tasks and their status
        - approve [task_id]: Approve a pending change
        - reject [task_id]: Reject a pending change
        - exit: Exit Cherry
        
        Natural language examples:
        - "Create a new Python module for handling file operations"
        - "Refactor the user authentication code to improve security"
        - "Explain how the data processing pipeline works"
        - "Add unit tests for the payment processing module"
        </cherry-output>
        """
        print(HTML(help_text))

    async def _show_status(self):
        """Show status of tasks in progress and pending approvals."""
        # Get pending approvals
        approvals = await self.orchestrator.get_pending_approvals()

        print(HTML("<cherry-output>Current Status:</cherry-output>"))

        if approvals:
            print(HTML("<cherry-output>Pending Approvals:</cherry-output>"))
            for task in approvals:
                task_id = task['task_id']
                task_type = task['task_type']
                print(HTML(
                    f"<cherry-output>- [{task_id}] {task_type}: awaiting your approval</cherry-output>"))
                # Show summary of changes if available
                if 'result' in task and 'summary' in task['result']:
                    print(
                        HTML(f"<cherry-output>  Summary: {task['result']['summary']}</cherry-output>"))
        else:
            print(HTML("<cherry-output>No pending approvals.</cherry-output>"))

        # Could also show task history and in-progress tasks here

    async def _approve_task(self, task_id: str, approved: bool):
        """Approve or reject a pending task."""
        action = "approved" if approved else "rejected"
        feedback = ""
        if not approved:
            feedback = await self.session.prompt_async(
                HTML('<prompt>Feedback for rejection (optional): </prompt>'),
                style=cherry_style
            )

        result = await self.orchestrator.approve_change(task_id, approved, feedback)

        if 'error' in result:
            print(HTML(f"<cherry-error>{result['error']}</cherry-error>"))
        else:
            print(
                HTML(f"<cherry-output>Task {task_id} has been {action}.</cherry-output>"))

    async def _process_natural_language(self, text: str):
        """Process natural language input and route to appropriate task."""
        print(HTML("<cherry-output>Processing your request...</cherry-output>"))

        # First, use the documentation agent to understand the request
        understanding_task = await self.orchestrator.submit_task(
            "understand_request",
            {
                "text": text,
                "requires_approval": False
            }
        )

        # Wait for understanding to complete
        while True:
            status = await self.orchestrator.get_task_status(understanding_task)
            if status['status'] in ['completed', 'failed']:
                break
            await asyncio.sleep(0.5)

        if status['status'] == 'failed':
            print(HTML(
                f"<cherry-error>Failed to understand request: {status.get('error', 'Unknown error')}</cherry-error>"))
            return

        # Extract the understood intent
        intent = status['result']['intent']
        print(HTML(
            f"<cherry-output>I understand you want to {intent['description']}.</cherry-output>"))

        # Submit the appropriate task based on intent
        if intent['type'] == 'code_generation':
            task_id = await self.orchestrator.submit_task(
                "code_generation",
                {
                    "description": text,
                    "intent": intent,
                    "requires_approval": True
                }
            )
            print(HTML(
                f"<cherry-output>I'll work on generating code for you. Task ID: {task_id}</cherry-output>"))

        elif intent['type'] == 'code_modification':
            task_id = await self.orchestrator.submit_task(
                "code_modification",
                {
                    "description": text,
                    "intent": intent,
                    "requires_approval": True
                }
            )
            print(HTML(
                f"<cherry-output>I'll work on modifying the code as requested. Task ID: {task_id}</cherry-output>"))

        elif intent['type'] == 'planning':
            task_id = await self.orchestrator.submit_task(
                "planning",
                {
                    "task_type": "breakdown",
                    "requirements": [text],
                    "requires_approval": False
                }
            )
            print(HTML(
                f"<cherry-output>I'm creating a plan for this. Task ID: {task_id}</cherry-output>"))

        elif intent['type'] == 'explanation':
            task_id = await self.orchestrator.submit_task(
                "explain",
                {
                    "query": text,
                    "requires_approval": False
                }
            )
            print(HTML(
                f"<cherry-output>I'm working on an explanation. Task ID: {task_id}</cherry-output>"))

        else:
            print(HTML(
                "<cherry-error>I'm not sure how to handle that request yet.</cherry-error>"))


def main():
    """Entry point for Cherry CLI."""
    parser = argparse.ArgumentParser(description='Cherry AI Assistant')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run the CLI
    cli = CherryCLI()
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(cli.setup())
        loop.run_until_complete(cli.start_interactive())
    except KeyboardInterrupt:
        print("\nShutting down Cherry...")
    finally:
        loop.run_until_complete(cli.orchestrator.stop())
        loop.close()


if __name__ == "__main__":
    main()
