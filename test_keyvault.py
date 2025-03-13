from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

KEY_VAULT_URL = "https://cherryai-kv.vault.azure.net/"
SECRET_NAME = "CherrySecret"

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

retrieved_secret = secret_client.get_secret(SECRET_NAME)

print(f"The secret '{SECRET_NAME}' is: {retrieved_secret.value}")
