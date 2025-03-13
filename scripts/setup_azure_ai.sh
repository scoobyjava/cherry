#!/bin/bash

echo "Setting up Azure AI assistance..."

# Make sure the AI examples extension is installed
az extension add --name ai-examples --only-show-errors || az extension update --name ai-examples

echo "You can now use Azure AI assistance with:"
echo "az find 'how to deploy a container to Azure Container Apps'"
echo ""
echo "Or try other queries like:"
echo "az find 'how to create a storage account'"
echo "az find 'how to set up a virtual machine'"
