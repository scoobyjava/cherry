#!/bin/bash

# Set variables
RESOURCE_GROUP=${RESOURCE_GROUP:-"cherry-resources"}
LOCATION=${LOCATION:-"eastus"}
CONTAINERAPPS_ENVIRONMENT="cherry-env"
CONTAINER_APP_NAME="cherry-app"
IMAGE_NAME=${IMAGE_NAME:-"mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"}
LOG_ANALYTICS_WORKSPACE="cherry-logs"

# Function to create Log Analytics workspace
create_log_analytics() {
    echo "Creating Log Analytics workspace..."
    az monitor log-analytics workspace create \
        --resource-group $RESOURCE_GROUP \
        --workspace-name $LOG_ANALYTICS_WORKSPACE \
        --location $LOCATION

    # Get the Log Analytics Client ID and Client Secret
    LOG_ANALYTICS_WORKSPACE_CLIENT_ID=$(az monitor log-analytics workspace show \
        --resource-group $RESOURCE_GROUP \
        --workspace-name $LOG_ANALYTICS_WORKSPACE \
        --query customerId \
        --output tsv)
    
    LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET=$(az monitor log-analytics workspace get-shared-keys \
        --resource-group $RESOURCE_GROUP \
        --workspace-name $LOG_ANALYTICS_WORKSPACE \
        --query primarySharedKey \
        --output tsv)
}

# Function to check if Container Apps environment exists
check_environment() {
    az containerapp env show --name $CONTAINERAPPS_ENVIRONMENT --resource-group $RESOURCE_GROUP &> /dev/null
    return $?
}

# Function to create Container Apps environment
create_environment() {
    echo "Creating Log Analytics workspace first..."
    create_log_analytics
    
    echo "Creating Container Apps environment..."
    az containerapp env create \
        --name $CONTAINERAPPS_ENVIRONMENT \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
        --logs-workspace-key $LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET
}

# Function to deploy container app
deploy_container_app() {
    echo "Deploying container app..."
    az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINERAPPS_ENVIRONMENT \
        --image $IMAGE_NAME \
        --target-port 80 \
        --ingress external
}

# Main script
echo "Deploying container to Azure Container Apps..."

# Check if containerapp extension is installed
if ! az extension show --name containerapp &> /dev/null; then
    echo "Installing Azure Container Apps extension..."
    az extension add --name containerapp --only-show-errors
fi

# Make sure the required resource provider is registered
echo "Ensuring required resource providers are registered..."
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait

# Check if environment exists, create if not
if ! check_environment; then
    create_environment
else
    echo "Container Apps environment already exists."
fi

# Wait for environment to be ready
echo "Waiting for environment to be ready..."
sleep 30

# Deploy container app
deploy_container_app

# Get the URL of the deployed app
APP_URL=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null)

if [ -n "$APP_URL" ]; then
    echo "Container app deployed successfully!"
    echo "You can access your app at: https://$APP_URL"
else
    echo "Container app deployment may have issues. Please check in the Azure portal."
fi
