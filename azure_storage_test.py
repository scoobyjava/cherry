import os
from azure.storage.blob import BlobServiceClient

# Retrieve the connection string from environment variables
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not conn_str:
    raise Exception("AZURE_STORAGE_CONNECTION_STRING is not set.")

# Create a BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(conn_str)

# Verify storage access by listing all containers
containers = blob_service_client.list_containers()
print("Available Containers:")
for container in containers:
    print(f"- {container['name']}")
