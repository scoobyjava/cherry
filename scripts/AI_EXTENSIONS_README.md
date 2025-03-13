# AI Extensions for GitHub Codespaces

This directory contains scripts to help you set up and use AI assistants in your GitHub Codespace.

## Available Scripts

- `setup_codespace_extensions.sh`: Installs and configures all necessary extensions
- `check_extensions.sh`: Checks if all extensions are properly installed
- `restart_vscode_server.sh`: Restarts the VS Code server if extensions aren't working
- `azure_login.sh`: Logs in to Azure
- `setup_azure_ai.sh`: Sets up Azure AI assistance

## Using AI Assistants

### GitHub Copilot
- Press `Ctrl+I` to get inline suggestions
- Open the Copilot Chat panel with `Ctrl+Shift+I`

### Sourcegraph Cody
- Click on the Cody icon in the sidebar
- Use `/` commands in the chat to perform specific actions

### Azure AI Assistance
- Use `az find 'your question here'` in the terminal

## Troubleshooting

If extensions aren't working:
1. Run `./scripts/check_extensions.sh` to verify installation
2. Run `./scripts/restart_vscode_server.sh` to restart the VS Code server
3. Refresh your browser to reconnect to the Codespace
