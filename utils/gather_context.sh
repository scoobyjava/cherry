#!/bin/bash

# Check if any arguments are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 file1 [file2 ...]"
    exit 1
fi

echo "Gathering context from specified files and directories..."

# Find all files in the specified paths, exclude unwanted directories, and process them
(
    find "$@" -type f -not -path '*/__pycache__/*' -not -path '*/.git/*' -print0 | sort -z -u | while IFS= read -r -d '' file; do
        # Check if the file is a text file
        if file -b --mime-type "$file" | grep -q '^text/'; then
            # Extract file extension to determine language
            ext="${file##*.}"
            case "$ext" in
                py) lang="python" ;;
                js) lang="javascript" ;;
                html) lang="html" ;;
                css) lang="css" ;;
                sh) lang="bash" ;;
                *) lang="" ;;
            esac
            # Output file header and content in Markdown format
            echo "--- file: $file ---"
            echo "\`\`\`$lang"
            cat "$file"
            echo "\`\`\`"
            echo ""
        fi
    done
) > context.txt

echo "Context saved to context.txt"