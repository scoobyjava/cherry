#!/bin/bash

# Script to setup GitHub integration for Cherry repository

set -e  # Exit on any error

# Check if repository URL is provided
if [ $# -eq 0 ]; then
    echo "Error: GitHub repository URL is required"
    echo "Usage: ./setup_github.sh <GITHUB_REPO_URL>"
    exit 1
fi

REPO_URL=$1
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Setting up GitHub integration for Cherry..."

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "Remote 'origin' already exists. Updating URL..."
    git remote set-url origin $REPO_URL
else
    echo "Adding remote 'origin'..."
    git remote add origin $REPO_URL
fi

echo "Pushing code to GitHub..."
git push -u origin $CURRENT_BRANCH

echo "Setup complete!"
echo "Your Cherry repository is now connected to: $REPO_URL"
echo "Branch '$CURRENT_BRANCH' is set up to track remote branch '$CURRENT_BRANCH' from 'origin'."
