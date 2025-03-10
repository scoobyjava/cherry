#!/bin/bash

# Check if API key is available
if [ -z "$SOURCEGRAPH_API_KEY" ]; then
  # Try to load from config file if environment variable isn't set
  if [ -f ~/.config/cody/credentials ]; then
    export SOURCEGRAPH_API_KEY=$(cat ~/.config/cody/credentials)
  else
    echo "Error: SOURCEGRAPH_API_KEY not found. Please set it up first."
    exit 1
  fi
fi

# Create config directory if it doesn't exist
mkdir -p ~/.config/cody

# Store credentials for future use
echo "$SOURCEGRAPH_API_KEY" > ~/.config/cody/credentials
chmod 600 ~/.config/cody/credentials

# Set up Cody configuration
cat > ~/.config/cody/config.json << EOF
{
  "endpoint": "https://sourcegraph.com",
  "username": "124418953-scoobyjava-xsjlr",
  "accessToken": "$SOURCEGRAPH_API_KEY",
  "avatarUrl": "https://avatars.githubusercontent.com/u/124418953?v=4"
}
EOF

echo "Successfully configured Cody AI with your credentials"

# Attempt to authenticate with Sourcegraph API
echo "Verifying authentication..."
curl -s -H "Authorization: token $SOURCEGRAPH_API_KEY" \
  https://sourcegraph.com/.api/graphql -d '{"query": "query { currentUser { username } }"}' | \
  grep -q "username" && echo "Authentication successful!" || echo "Authentication failed. Please check your API key."
