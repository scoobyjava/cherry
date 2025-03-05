#!/bin/bash

echo "Removing Codeium extension and references..."

# Uninstall Codeium extension if VS Code is available
if command -v code &> /dev/null; then
    echo "Uninstalling Codeium extension from VS Code..."
    code --uninstall-extension Codeium.codeium || echo "Extension not found or could not be uninstalled"
else
    echo "VS Code CLI not found. Please manually uninstall Codeium extension from VS Code"
fi

# Find and list all files containing "codeium" references
echo "Finding all files with Codeium references..."
CODEIUM_FILES=$(grep -ril "codeium" /workspaces/cherry || echo "")

if [ -z "$CODEIUM_FILES" ]; then
    echo "No files with Codeium references found."
else
    echo "Found the following files with Codeium references:"
    echo "$CODEIUM_FILES"
    
    echo "Would you like to review and remove these references? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        for file in $CODEIUM_FILES; do
            echo "Processing $file..."
            # Check if file is a configuration file that might need special handling
            if [[ "$file" == *".json" || "$file" == *".yaml" || "$file" == *".yml" ]]; then
                echo "This is a configuration file. Please review manually."
            else
                # Create backup
                cp "$file" "$file.backup"
                # Remove lines containing "codeium"
                grep -v "codeium" "$file.backup" > "$file"
                echo "Removed Codeium references from $file (backup created at $file.backup)"
            fi
        done
    fi
fi

echo "Codeium removal process completed."
