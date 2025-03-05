import openai
import os
import asyncio
import datetime  # newly added import
import requests  # newly added for API calls
from async_task_manager import TaskManager  # Newly created async task manager
from agent_manager import AgentManager  # Newly created agent manager

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def log_event(message):
    print(f"{datetime.datetime.now().isoformat()} - {message}")


def ask_openai(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Added asynchronous wrapper for ask_openai


async def ask_openai_async(prompt):
    return await asyncio.to_thread(ask_openai, prompt)

# Define an async task that queries OpenAI and prints the result


def create_openai_task(prompt):
    async def task():
        log_event(f"Task assigned for prompt: {prompt}")
        result = await ask_openai_async(prompt)
        print(f"Prompt: {prompt}\nResponse: {result}")
        log_event(f"Task completed for prompt: {prompt}")
    return task

# New: Example agent implementation demonstrating dynamic callback registration


class ExampleAgent:
    def __init__(self):
        self.name = "ExampleAgent"

    def callback(self, data):
        log_event(f"Agent {self.name} received task data: {data}")
        print(f"{self.name} processed: {data}")
        log_event(f"Agent {self.name} completed processing task data: {data}")

    def register(self, manager):
        manager.register_agent(self.name, self.callback)


def query_grok_api(prompt):
    # Sends a prompt to the Grok AI API and returns the result.
    # Replace with the actual Grok AI API endpoint
    url = "https://api.grok.ai/v1/query"
    try:
        response = requests.post(url, json={"prompt": prompt}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("result")
    except requests.exceptions.RequestException as e:
        log_event(f"Grok API request error: {e}")
        return None


if __name__ == "__main__":
    async def main():
        manager = TaskManager()
        # Queue tasks to process in order
        prompts = [
            "Explain the purpose of the PlanningAgent class in the Cherry AI project.",
            "Describe the architecture of the Cherry AI system."
        ]
        for prompt in prompts:
            await manager.add_task(create_openai_task(prompt))
        asyncio.create_task(manager.run(workers=1))

        # Dynamically initialize agents
        agent_manager = AgentManager()
        # List of agents that implement their own 'register' method
        agents = [ExampleAgent()  # ...additional agents can be added here...
                  ]
        registered_agents = agent_manager.initialize_agents(agents)
        print("Registered agents:", list(registered_agents.keys()))

        # Keeping the main loop alive if needed
        await asyncio.sleep(1)

    asyncio.run(main())
