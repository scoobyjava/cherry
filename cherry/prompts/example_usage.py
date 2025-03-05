"""
Example usage of the code generation prompt template.
"""
from prompt_loader import create_code_generation_prompt

# Basic usage example
prompt = create_code_generation_prompt(
    description="Create a function that sorts a list of dictionaries based on a specified key",
    language="Python",
    requirements=[
        "The function should take a list of dictionaries and a key name as parameters",
        "It should handle cases where the key doesn't exist in some dictionaries",
        "The function should allow sorting in ascending or descending order"
    ],
    framework="None",
    additional_context="This will be used in a data processing pipeline where performance is important."
)

print(prompt)

# More complex example
advanced_prompt = create_code_generation_prompt(
    description="Implement a REST API endpoint that handles user registration",
    language="JavaScript",
    requirements=[
        "Validate email format and password strength",
        "Check for duplicate users in the database",
        "Return appropriate HTTP status codes and error messages"
    ],
    framework="Express.js with MongoDB",
    additional_context="This endpoint will be part of an authentication service in a microservice architecture."
)

print("\n\n" + advanced_prompt)
