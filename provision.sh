#!/bin/bash
# ...existing code...
az login

RESOURCE_GROUP="cherry-rg"
AKS_CLUSTER="cherry-aks"
LOCATION="westus2"

# Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create AKS cluster with autoscaling enabled
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --location $LOCATION \
  --node-count 2 \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 10 \
  --generate-ssh-keys

# Connect to the AKS cluster
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER
# ...existing code...