import asyncio
import sys
import os
import logging
import uuid
import argparse
from typing import Dict, Any

from cherry.agents.language_agent import LanguageAgent
from cherry.agents.planning_agent import PlanningAgent
from cherry.agents.coding_agent import CodingAgent
from cherry.integrations.copilot_integration import CopilotIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CherryCLI:
    """
    Command-line interface for interacting with Cherry using natural language.

    This provides a text-based interaction system where you can:
    1. Enter natural language requests
    2. Receive code proposals from Cherry
    3. Approve or reject proposals
    4. Get deployment recommendations from GitHub Copilot
    """

    def __init__(self):
        """Initialize the CLI with required agents."""
        self.language_agent = LanguageAgent()
        self.planning_agent = PlanningAgent(
            "Planning Agent", "Creates development plans and task breakdowns")
        self.coding_agent = CodingAgent(
            "Coding Agent", "Generates and modifies code based on requirements")
        self.copilot_integration = CopilotIntegration()

        # Register specialized agents with the language agent
        self.language_agent.register_agent("planning", self.planning_agent)
        self.language_agent.register_agent("coding", self.coding_agent)

        self.session_id = str(uuid.uuid4())
        self.last_proposal = None

    async def start_interactive_session(self):
        """Start an interactive CLI session."""
        print("\n🍒 Welcome to Cherry! I'm your AI coding assistant.")
        print("Type 'exit' or 'quit' to end the session.")
        print("Type 'help' for available commands.")

        while True:
            try:
                # Get user input
                user_input = input("\n🍒 How can I help you? > ").strip()

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 Goodbye! Have a great day!")
                    break

                # Check for help command
                if user_input.lower() == 'help':
                    self._show_help()
                    continue

                # Check for special commands
                if user_input.startswith('!'):
                    await self._handle_command(user_input[1:])
                    continue

                # Process the input
                result = await self._process_input(user_input)

                # Display the response
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"\n{result['response']}")

                    # If this was a coding request and we have a proposal
                    if result.get('intent') == 'coding' and 'code_proposal' in result.get('details', {}):
                        self.last_proposal = result['details']['code_proposal']
                        print("\n📝 Code proposal generated. Would you like to: ")
                        print("  1. View the proposal")
                        print("  2. Approve and get deployment advice from Copilot")
                        print("  3. Reject and start over")

                        choice = input("Enter your choice (1-3): ").strip()
                        await self._handle_proposal_choice(choice)

            except KeyboardInterrupt:
                print("\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in CLI session: {e}")
                print(f"❌ An unexpected error occurred: {str(e)}")

    async def _process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input through the language agent."""
        task_data = {
            "user_input": user_input,
            "session_id": self.session_id
        }
        return await self.language_agent.process(task_data)

    async def _handle_command(self, command: str):
        """Handle special commands starting with '!'."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            print("🍒 Screen cleared!")
        elif cmd == 'history':
            self._show_history()
        elif cmd == 'save' and self.last_proposal and len(parts) > 1:
            filepath = parts[1]
            self._save_proposal(filepath)
        else:
            print("❌ Unknown command. Type 'help' for available commands.")

    def _show_help(self):
        """Display help information."""
        print("\n🍒 Cherry CLI Help:")
        print("  - Enter natural language requests to get assistance")
        print("  - Special commands:")
        print("    !clear     - Clear the screen")
        print("    !history   - Show conversation history")
        print("    !save PATH - Save the last code proposal to a file")
        print("  - When viewing a proposal, you can approve it to get deployment advice")

    def _show_history(self):
        """Show conversation history."""
        print("\n📜 Conversation History:")
        for idx, msg in enumerate(self.language_agent._conversation_history):
            role = "🧑" if msg["role"] == "user" else "🍒"
            print(
                f"{idx+1}. {role} {msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''}")

    def _save_proposal(self, filepath: str):
        """Save the last code proposal to a file."""
        if not self.last_proposal:
            print("❌ No code proposal to save!")
            return

        try:
            with open(filepath, 'w') as f:
                f.write(self.last_proposal['code'])
            print(f"✅ Proposal saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving proposal: {str(e)}")

    async def _handle_proposal_choice(self, choice: str):
        """Handle user choice for a code proposal."""
        if not self.last_proposal:
            print("❌ No active proposal to handle!")
            return

        if choice == '1':
            # View the proposal
            print("\n📝 Code Proposal:")
            print(f"Files to modify: {len(self.last_proposal['files'])}")
            for file_info in self.last_proposal['files']:
                print(f"\nFile: {file_info['path']}")
                print("```")
                print(file_info['content'])
                print("```")
        elif choice == '2':
            # Approve and get deployment advice
            print(
                "\n✅ Proposal approved! Getting deployment advice from GitHub Copilot...")
            try:
                advice = await self.copilot_integration.get_deployment_advice(self.last_proposal)
                print("\n🚀 Deployment Advice from GitHub Copilot:")
                print(advice)
            except Exception as e:
                logger.error(f"Error getting deployment advice: {e}")
                print(f"❌ Error getting deployment advice: {str(e)}")
        elif choice == '3':
            # Reject and start over
            print("\n❌ Proposal rejected. You can make a new request.")
            self.last_proposal = None
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.")


def main():
    """Run the Cherry CLI."""
    parser = argparse.ArgumentParser(
        description="Cherry CLI - Natural language coding assistant")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Set the logging level")
    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Run the CLI
    cli = CherryCLI()
    asyncio.run(cli.start_interactive_session())


if __name__ == "__main__":
    main()
