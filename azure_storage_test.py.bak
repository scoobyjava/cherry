<<<<<<< Tabnine <<<<<<<
import os
from azure.storage.blob import BlobServiceClient

# Retrieve the connection string from environment variables#-
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")#-
# Get connection string from environment variable (populated from GitHub secrets)#+
conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")#+
if not conn_str:
    raise Exception("AZURE_STORAGE_CONNECTION_STRING is not set.")#-
    raise Exception("AZURE_STORAGE_CONNECTION_STRING is not set in environment variables.")#+

# Create a BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(conn_str)

# Verify storage access by listing all containers#-
containers = blob_service_client.list_containers()#-
print("Available Containers:")#-
for container in containers:#-
    print(f"- {container['name']}")#-
# Test connection#+
def test_connection():#+
    try:#+
        # List the containers to verify connection#+
        containers = list(blob_service_client.list_containers(max_results=5))#+
        print(f"Successfully connected to Azure Storage. Found {len(containers)} containers.")#+
        return True#+
    except Exception as e:#+
        print(f"Failed to connect to Azure Storage: {str(e)}")#+
        return False#+
#+
if __name__ == "__main__":#+
    test_connection()#+
>>>>>>> Tabnine >>>>>>># {"source":"chat"}
