#!/bin/bash

echo "Checking if extensions are running..."

# Check GitHub Copilot
if code --list-extensions | grep -q "GitHub.copilot"; then
    echo "✅ GitHub Copilot is installed"
else
    echo "❌ GitHub Copilot is not installed"
fi

# Check Sourcegraph Cody
if code --list-extensions | grep -q "sourcegraph.cody-ai"; then
    echo "✅ Sourcegraph Cody is installed"
else
    echo "❌ Sourcegraph Cody is not installed"
fi

# Check Azure extensions
if code --list-extensions | grep -q "ms-vscode.azure-account"; then
    echo "✅ Azure Account extension is installed"
else
    echo "❌ Azure Account extension is not installed"
fi

# Check Azure CLI
if command -v az &> /dev/null; then
    echo "✅ Azure CLI is installed"
    echo "Azure CLI version: $(az --version | head -n 1)"
    
    # Check Azure CLI extensions
    if az extension list --output json | grep -q "containerapp"; then
        echo "✅ Azure Container Apps extension is installed"
    else
        echo "❌ Azure Container Apps extension is not installed"
    fi
    
    if az extension list --output json | grep -q "ai-examples"; then
        echo "✅ Azure AI Examples extension is installed"
    else
        echo "❌ Azure AI Examples extension is not installed"
    fi
else
    echo "❌ Azure CLI is not installed"
fi

echo ""
echo "To use Azure AI assistance, try:"
echo "az find 'how to deploy a container to Azure Container Apps'"
echo ""
echo "To use GitHub Copilot, press Ctrl+I in a code file"
echo ""
echo "To use Sourcegraph Cody, click on the Cody icon in the sidebar"
