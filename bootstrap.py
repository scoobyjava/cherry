import requests

TASKS = [
    "Set up Kubernetes cluster on GCP",
    "Create API connections for OpenAI, Pinecone, Zilliz",
    "Deploy Cherry’s API to Railway",
    "Create Terraform configuration for automated deployment",
]

for task in TASKS:
    response = requests.post("http://127.0.0.1:8080/generate-code/", json={"task": task})
    print(f"Task: {task} -> {response.json()}")
