#!/bin/bash

# Run the Azure login script directly
if [ -f "/workspaces/cherry/scripts/azure_login.sh" ]; then
    echo "Running Azure login script..."
    /workspaces/cherry/scripts/azure_login.sh
else
    echo "Azure login script not found. Creating it..."
    mkdir -p /workspaces/cherry/scripts
    cat > /workspaces/cherry/scripts/azure_login.sh << 'INNEREOF'
#!/bin/bash

# Check if already logged in
az account show &> /dev/null
if [ $? -eq 0 ]; then
    echo "Already logged in to Azure."
    exit 0
fi

# Try to login silently
echo "Attempting to login to Azure..."
az login --use-device-code

# Check if login was successful
if [ $? -eq 0 ]; then
    echo "Successfully logged in to Azure."
    
    # Set environment variables
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    TENANT_ID=$(az account show --query tenantId -o tsv)
    
    export AZURE_SUBSCRIPTION_ID="$SUBSCRIPTION_ID"
    export AZURE_TENANT_ID="$TENANT_ID"
    
    echo "Azure environment variables set:"
    echo "Subscription ID: $SUBSCRIPTION_ID"
    echo "Tenant ID: $TENANT_ID"
else
    echo "Failed to login to Azure. Please run 'az login' manually."
fi
INNEREOF
    chmod +x /workspaces/cherry/scripts/azure_login.sh
    /workspaces/cherry/scripts/azure_login.sh
fi
