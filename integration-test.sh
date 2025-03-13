#!/bin/bash
set -e

# ...existing code: environment configuration...

# Check required environment variables
: "${AZ_KEY_VAULT:?AZ_KEY_VAULT not set}"
: "${AZ_AKS_RESOURCE_GROUP:?AZ_AKS_RESOURCE_GROUP not set}"
: "${AZ_AKS_CLUSTER:?AZ_AKS_CLUSTER not set}"
: "${AZ_APPINSIGHTS:?AZ_APPINSIGHTS not set}"
: "${AZ_STORAGE_ACCOUNT:?AZ_STORAGE_ACCOUNT not set}"

# Test Azure Key Vault secret retrieval
echo "Testing Azure Key Vault..."
secret=$(az keyvault secret show --vault-name "$AZ_KEY_VAULT" --name "test-secret" --query value -o tsv) || { echo "Failed to retrieve secret from Key Vault"; exit 1; }
echo "Key Vault test passed."

# Test AKS deployment and connectivity
echo "Testing AKS deployment..."
kubectl config use-context "$AZ_AKS_CLUSTER" || { echo "Kube context $AZ_AKS_CLUSTER not found"; exit 1; }
replicas_ready=$(kubectl get deployment cherry-ai -n default -o jsonpath='{.status.readyReplicas}') || { echo "Failed to get deployment status"; exit 1; }
if [[ "$replicas_ready" -lt 1 ]]; then
    echo "AKS deployment is not healthy"
    exit 1
fi
echo "AKS deployment test passed."

# Test Application Insights connectivity
echo "Testing Application Insights..."
insights_app_id=$(az monitor app-insights component show --app "$AZ_APPINSIGHTS" --resource-group "$AZ_AKS_RESOURCE_GROUP" --query "applicationId" -o tsv) || { echo "Failed to query Application Insights"; exit 1; }
if [ -z "$insights_app_id" ]; then
  echo "Application Insights is not responsive"
  exit 1
fi
echo "Application Insights test passed."

# Test Azure Storage connectivity
echo "Testing Azure Storage..."
storage_check=$(az storage blob list --account-name "$AZ_STORAGE_ACCOUNT" --container-name "test-container" --query "[0]" -o tsv) || { echo "Failed to list blobs in Azure Storage"; exit 1; }
echo "Azure Storage test passed."

echo "All integration tests passed successfully."
