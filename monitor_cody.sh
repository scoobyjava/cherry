#!/bin/bash
set -e

LOG="/workspaces/your-repo/cody.log"
MAX_RETRIES=3

LOG_PATH="/workspaces/cherry/cody.log"

# Check process status
if ! pgrep -f "cody serve" > /dev/null; then
  echo "$(date) - Service down. Restarting..." >> "$LOG"
  for ((i=1; i<=MAX_RETRIES; i++)); do
    nohup cody serve --debug >> "$LOG" 2>&1 &
    sleep 5
    if pgrep -f "cody serve" >/dev/null; then
      echo "$(date) - Restart successful" >> "$LOG"
      exit 0
    fi
  done
  echo "$(date) - Critical failure after $MAX_RETRIES attempts" >> "$LOG"
  exit 1
fi

# Validate authentication
if ! cody whoami | grep -q "124418953-scoobyjava-xsjir"; then
  echo "$(date) - Reauthenticating..." >> "$LOG"
  cody configure --endpoint https://sourcegraph.com --access-token "$SOURCECODE_API_KEY" --force
fi
