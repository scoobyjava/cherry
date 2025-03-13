#!/bin/bash

# Set variables
RESOURCE_GROUP=${RESOURCE_GROUP:-"cherry-resources"}
LOCATION=${LOCATION:-"eastus"}
OPENAI_NAME="cherry-openai"

# Function to check if Azure OpenAI service exists
check_openai_service() {
    az cognitiveservices account show --name $OPENAI_NAME --resource-group $RESOURCE_GROUP &> /dev/null
    return $?
}

# Function to create Azure OpenAI service
create_openai_service() {
    echo "Creating Azure OpenAI service..."
    az cognitiveservices account create \
        --name $OPENAI_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --kind OpenAI \
        --sku S0 \
        --yes
    
    echo "Deploying GPT model..."
    az cognitiveservices account deployment create \
        --name $OPENAI_NAME \
        --resource-group $RESOURCE_GROUP \
        --deployment-name gpt-35-turbo \
        --model-name gpt-35-turbo \
        --model-version "0301" \
        --model-format OpenAI \
        --sku Standard \
        --capacity 1
}

# Main script
echo "Setting up Azure AI assistance for Cherry project..."

# Check if cognitive services extension is installed
if ! az extension show --name cognitiveservices &> /dev/null; then
    echo "Installing Azure Cognitive Services extension..."
    az extension add --name cognitiveservices --only-show-errors
fi

# Check if OpenAI service exists, create if not
if ! check_openai_service; then
    create_openai_service
else
    echo "Azure OpenAI service already exists."
fi

# Get the endpoint and key
ENDPOINT=$(az cognitiveservices account show --name $OPENAI_NAME --resource-group $RESOURCE_GROUP --query properties.endpoint -o tsv)
KEY=$(az cognitiveservices account keys list --name $OPENAI_NAME --resource-group $RESOURCE_GROUP --query key1 -o tsv)

echo "Azure OpenAI service is ready to use."
echo "Endpoint: $ENDPOINT"
echo "Key: $KEY (Keep this secure!)"
echo ""
echo "You can now use this service in your Cherry project."
