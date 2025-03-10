#!/bin/bash
# autosave.sh – commit and push any unstaged changes

# Change to the directory where the script is located
cd "$(dirname "$0")" || exit 1

# Add all changes
git add .

# Check if there are any changes staged for commit
if ! git diff --cached --quiet; then
  # Commit with a timestamp in the message
  git commit -m "Autosave commit: $(date +'%Y-%m-%d %H:%M:%S')"
  # Push the commit to the current branch
  git push
  echo "Autosave complete at $(date)"
else
  echo "No changes to commit at $(date)"
fi
