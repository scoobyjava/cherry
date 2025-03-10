#!/bin/bash
#!/bin/bash
# Create the login script if it doesn't exist
if [ ! -f ~/cody-login.sh ]; then# Make the login script executable
  cat > ~/cody-login.sh << 'EOF'
#!/bin/bash
if [ -f ~/.config/cody/credentials ]; then# Securely request and store the API key if not already set
  export SOURCEGRAPH_API_KEY=$(cat ~/.config/cody/credentials)redentials ]; then
  echo "Cody AI authentication complete."
else
  echo "Error: Credentials file not found."fig/cody
finfig/cody/credentials
EOF
fi

# Make the login script executable# Set up autostart for various environments
chmod +x ~/cody-login.sh

# Securely request and store the API key if not already set# Create desktop entry for auto-login
if [ -z "$SOURCEGRAPH_API_KEY" ] && [ ! -f ~/.config/cody/credentials ]; thendesktop << EOF
  echo "Please enter your Sourcegraph API key (it will be stored securely):"
  read -s api_keyn
  mkdir -p ~/.config/codyin
  echo "$api_key" > ~/.config/cody/credentialsgin.sh
  chmod 600 ~/.config/cody/credentials
filse
rt-enabled=true
# Set up autostart for various environmentso Cody AI
mkdir -p ~/.config/autostart

# Create desktop entry for auto-login# Add to .bashrc and .zshrc for terminal sessions
cat > ~/.config/autostart/cody-login.desktop << EOF
[Desktop Entry]
Type=ApplicationH_API_KEY" "$rc_file"; then
Name=Cody AI Login
Exec=$HOME/cody-login.shrcegraph API key" >> "$rc_file"
Hidden=falsedy/credentials 2>/dev/null || echo '')" >> "$rc_file"
NoDisplay=false
X-GNOME-Autostart-enabled=trueoken \$SOURCEGRAPH_API_KEY\" https://sourcegraph.com/.api/graphql -d '{\"query\": \"query { currentUser { username } }\"}' | grep -q \"username\"; then" >> "$rc_file"
Comment=Automatically log in to Cody AI
EOF

# Add to .bashrc and .zshrc for terminal sessions
for rc_file in ~/.bashrc ~/.zshrc; do
  if [ -f "$rc_file" ]; then
    if ! grep -q "SOURCEGRAPH_API_KEY" "$rc_file"; thenecho "Setup complete! Cody AI will automatically authenticate on login."
      echo "" >> "$rc_file"
      echo "# Auto-load Sourcegraph API key" >> "$rc_file"      echo "export SOURCEGRAPH_API_KEY=\$(cat ~/.config/cody/credentials 2>/dev/null || echo '')" >> "$rc_file"
      echo "# Run Cody login if not already authenticated" >> "$rc_file"
      echo "if [ -f ~/cody-login.sh ] && ! curl -s -H \"Authorization: token \$SOURCEGRAPH_API_KEY\" https://sourcegraph.com/.api/graphql -d '{\"query\": \"query { currentUser { username } }\"}' | grep -q \"username\"; then" >> "$rc_file"
      echo "  ~/cody-login.sh" >> "$rc_file"
      echo "fi" >> "$rc_file"
    fi
  fi
done

# Verify the connection to Sourcegraph
echo "Verifying connection to Sourcegraph..."
if [ -f ~/.config/cody/credentials ]; then
  api_key=$(cat ~/.config/cody/credentials)
  if curl -s -H "Authorization: token $api_key" https://sourcegraph.com/.api/graphql -d '{"query": "query { currentUser { username } }"}' | grep -q "username"; then
    echo "✅ Connection to Sourcegraph verified successfully!"
  else
    echo "❌ Could not connect to Sourcegraph. Please check your API key."
  fi
fi

echo "Setup complete! Cody AI will automatically authenticate on login."
echo "You can also manually run ~/cody-login.sh at any time."
echo "No rebuild is required - the setup is complete."
