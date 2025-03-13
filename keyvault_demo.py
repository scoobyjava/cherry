import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Replace with the name of your secret in Key Vault
secret_name = "YOUR_SECRET_NAME"

# URL for your Key Vault
key_vault_url = "https://cherryai-kv.vault.azure.net/"

# Authenticate using DefaultAzureCredential (ensure proper Azure environment configuration)
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)


def get_secret_value(secret_name):
    retrieved_secret = client.get_secret(secret_name)
    return retrieved_secret.value


if __name__ == "__main__":
    secret_value = get_secret_value(secret_name)
    print(f"Retrieved secret value: {secret_value}")
