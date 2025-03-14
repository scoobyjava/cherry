<<<<<<< Tabnine <<<<<<<
# This file has been updated to use GitHub organizational secrets instead of Azure Key Vault#+
import os
from azure.identity import DefaultAzureCredential#-
from azure.keyvault.secrets import SecretClient#-

# Replace with the name of your secret in Key Vault#-
# Replace with the name of your secret#+
secret_name = "YOUR_SECRET_NAME"

# URL for your Key Vault#-
key_vault_url = "https://cherryai-kv.vault.azure.net/"#-
#-
# Authenticate using DefaultAzureCredential (ensure proper Azure environment configuration)#-
credential = DefaultAzureCredential()#-
client = SecretClient(vault_url=key_vault_url, credential=credential)#-
def get_secret_value(secret_name):
    retrieved_secret = client.get_secret(secret_name)#-
    return retrieved_secret.value#-
    """#+
    Get a secret value from environment variables#+
    (populated from GitHub organizational secrets)#+
    """#+
    secret_value = os.environ.get(secret_name)#+
    if not secret_value:#+
        raise ValueError(f"Secret '{secret_name}' not found in environment variables")#+
    return secret_value#+


if __name__ == "__main__":
    secret_value = get_secret_value(secret_name)#-
    print(f"Retrieved secret value: {secret_value}")#-
    try:#+
        secret_value = get_secret_value(secret_name)#+
        print(f"Retrieved secret value: {secret_value}")#+
    except Exception as e:#+
        print(f"Error retrieving secret: {str(e)}")#+
>>>>>>> Tabnine >>>>>>># {"source":"chat"}
