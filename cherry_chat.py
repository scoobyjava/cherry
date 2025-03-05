#!/usr/bin/env python3
from cherry.cli import CherryCLI
import os
import sys
import asyncio
import argparse
import logging

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_environment():
    """Setup the environment for Cherry."""
    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable is not set.")
        print("Some functionality may be limited.")

        # Option to set the API key
        api_key = input(
            "Enter your OpenAI API key (leave empty to continue anyway): ").strip()
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            print("API key set for this session.")
        else:
            print("Continuing without API key...")


def main():
    """Main entry point for Cherry Chat."""
    parser = argparse.ArgumentParser(
        description="Cherry Chat - An AI coding assistant")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Setup environment
    setup_environment()

    # Start the CLI
    cli = CherryCLI()
    try:
        asyncio.run(cli.start_interactive_session())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logging.error(f"Error in main application: {e}")
        print(f"❌ An error occurred: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
