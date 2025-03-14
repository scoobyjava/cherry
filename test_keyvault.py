# This file has been updated to use GitHub organizational secrets instead of Azure Key Vault
import os

SECRET_NAME = "CherrySecret"

# Get secret from environment variables
secret_value = os.environ.get(SECRET_NAME)

if secret_value:
    print(f"The secret '{SECRET_NAME}' is: {secret_value}")
else:
    print(f"Secret '{SECRET_NAME}' not found in environment variables")
