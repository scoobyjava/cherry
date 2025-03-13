#!/bin/bash

# Check if Azure Copilot extension is installed
if ! az extension show --name copilot &> /dev/null; then
    echo "Installing Azure Copilot extension..."
    az extension add --name copilot --only-show-errors
fi

# Function to ask Azure Copilot
ask_copilot() {
    echo "Asking Azure Copilot: $1"
    az copilot "$1"
}

# Check if a question was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"Your question for Azure Copilot\""
    echo "Example: $0 \"How do I create a container app?\""
    exit 1
fi

# Ask the question
ask_copilot "$1"
