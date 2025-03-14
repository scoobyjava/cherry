<<<<<<< Tabnine <<<<<<<
from azure.identity import DefaultAzureCredential#-
from azure.keyvault.secrets import SecretClient#-
# This file has been updated to use GitHub organizational secrets instead of Azure Key Vault#+
import os#+

KEY_VAULT_URL = "https://cherryai-kv.vault.azure.net/"#-
SECRET_NAME = "CherrySecret"

credential = DefaultAzureCredential()#-
secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)#-
# Get secret from environment variables#+
secret_value = os.environ.get(SECRET_NAME)#+

retrieved_secret = secret_client.get_secret(SECRET_NAME)#-
#-
print(f"The secret '{SECRET_NAME}' is: {retrieved_secret.value}")#-
if secret_value:#+
    print(f"The secret '{SECRET_NAME}' is: {secret_value}")#+
else:#+
    print(f"Secret '{SECRET_NAME}' not found in environment variables")#+
>>>>>>> Tabnine >>>>>>># {"source":"chat"}
