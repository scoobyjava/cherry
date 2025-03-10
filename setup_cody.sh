#!/bin/bash
set -e

# Configure Cody CLI with automatic authentication
cody configure \
  --endpoint https://sourcegraph.com \
  --access-token "$SOURCECODE_API_KEY" \
  --debug

# Start Cody service and keep it running; log output to cody.log
nohup cody serve --debug > /workspaces/your-repo/cody.log 2>&1 &

# Verify service status
sleep 5
if pgrep -f "cody serve" > /dev/null; then
  echo "✅ Cody AI active | PID: $(pgrep -f 'cody serve')"
else
  echo "❌ Startup failed - check cody.log"
  exit 1
fi

{
  "postCreateCommand": "/workspaces/your-repo/setup_cody.sh",
  "customizations": {
    "codespaces": {
      "env": {
        "SOURCECODE_API_KEY": "${{ secrets.SOURCECODE_API_KEY }}"
      }
    }
  }
}
