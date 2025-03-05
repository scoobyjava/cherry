import asyncio
import argparse
import sys
import time

# ...existing Cherry imports...
from cherry.staging.staging_deployment import StagingDeploymentAgent


async def process_command(command: str):
    print(f"Processing command: {command}")
    # Here you would convert the natural language command into a task.
    # For demonstration, we assume the command directly maps to a task.
    task = {"feature": command, "details": "Command executed via CLI"}
    agent = StagingDeploymentAgent()
    print("Starting task execution...")
    result = await agent.handle_deployment(task)
    print("Task completed.")
    print("Result:", result)


def main():
    parser = argparse.ArgumentParser(description="Cherry CLI Interface")
    parser.add_argument("command", type=str,
                        help="Natural language command for Cherry")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_command(args.command))


if __name__ == "__main__":
    main()
