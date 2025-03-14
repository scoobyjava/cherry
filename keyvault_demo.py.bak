# This file has been updated to use GitHub organizational secrets instead of Azure Key Vault
import os

# Replace with the name of your secret
secret_name = "YOUR_SECRET_NAME"

def get_secret_value(secret_name):
    """
    Get a secret value from environment variables
    (populated from GitHub organizational secrets)
    """
    secret_value = os.environ.get(secret_name)
    if not secret_value:
        raise ValueError(f"Secret '{secret_name}' not found in environment variables")
    return secret_value


if __name__ == "__main__":
    try:
        secret_value = get_secret_value(secret_name)
        print(f"Retrieved secret value: {secret_value}")
    except Exception as e:
        print(f"Error retrieving secret: {str(e)}")
