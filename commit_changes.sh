#!/bin/bash

# Make scripts executable
chmod +x setup_structure.sh
chmod +x remove_codeium.sh

# Initialize git repo if not already done
if [ ! -d ".git" ]; then
    git init
    echo "Git repository initialized"
fi

# Add all changes
git add .

# Commit the changes
git commit -m "Organize project structure and remove Codeium references"

# Instructions for pushing
echo "Changes committed successfully. To push to your remote repository, run:"
echo "git push origin <your-branch-name>"
