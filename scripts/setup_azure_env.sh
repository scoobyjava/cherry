#!/bin/bash

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI not found. Installing..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Login to Azure if not already logged in
az account show &> /dev/null
if [ $? -ne 0 ]; then
    echo "Not logged in to Azure. Logging in..."
    az login --use-device-code
fi

# Install useful Azure extensions
echo "Installing Azure extensions..."
az extension add --name azure-devops --only-show-errors || echo "Azure DevOps extension already installed"
az extension add --name containerapp --only-show-errors || echo "Container App extension already installed"

# Set environment variables
echo "Setting Azure environment variables..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

# Add to both .bashrc and current environment
echo "export AZURE_SUBSCRIPTION_ID=\"$SUBSCRIPTION_ID\"" >> ~/.bashrc
echo "export AZURE_TENANT_ID=\"$TENANT_ID\"" >> ~/.bashrc
export AZURE_SUBSCRIPTION_ID="$SUBSCRIPTION_ID"
export AZURE_TENANT_ID="$TENANT_ID"

echo "Azure environment setup complete!"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Tenant ID: $TENANT_ID"
