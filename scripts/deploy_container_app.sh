#!/bin/bash

# Set variables
RESOURCE_GROUP=${RESOURCE_GROUP:-"cherry-resources"}
LOCATION=${LOCATION:-"eastus"}
CONTAINERAPPS_ENVIRONMENT="cherry-env"
CONTAINER_APP_NAME="cherry-app"
IMAGE_NAME=${IMAGE_NAME:-"mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"}

# Function to check if Container Apps environment exists
check_environment() {
    az containerapp env show --name $CONTAINERAPPS_ENVIRONMENT --resource-group $RESOURCE_GROUP &> /dev/null
    return $?
}

# Function to create Container Apps environment
create_environment() {
    echo "Creating Container Apps environment..."
    az containerapp env create \
        --name $CONTAINERAPPS_ENVIRONMENT \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
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

# Check if environment exists, create if not
if ! check_environment; then
    create_environment
else
    echo "Container Apps environment already exists."
fi

# Deploy container app
deploy_container_app

# Get the URL of the deployed app
APP_URL=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

echo "Container app deployed successfully!"
echo "You can access your app at: https://$APP_URL"
