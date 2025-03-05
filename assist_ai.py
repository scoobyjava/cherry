import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def ask_openai(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()


if __name__ == "__main__":
    prompt = "Explain the purpose of the PlanningAgent class in the Cherry AI project."
    answer = ask_openai(prompt)
    print(answer)
```

name: Assist AI

on:
    push:
        branches:
            - main
    pull_request:
        branches:
            - main

jobs:
    assist:
        runs-on: ubuntu-latest
        steps:
            - name: Checkout code
               uses: actions/checkout@v2

            - name: Set up Python
               uses: actions/setup-python@v2
                with:
                    python-version: '3.8'

            - name: Install dependencies
               run: |
                   pip install openai

            - name: Run Assist AI script
               env:
                    OPENAI_API_KEY: ${{secrets.OPENAI_API_KEY}}
                run: |
                    python / workspaces/cherry/assist_ai.py