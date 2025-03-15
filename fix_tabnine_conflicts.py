<<<<<<< Tabnine <<<<<<<
#!/usr/bin/env python3
"""
Script to automatically resolve Tabnine merge conflicts by keeping the newer code.
This script will look for Tabnine merge conflict markers and resolve them by:
1. For files with #+/- markers: Keep the lines with #+ and remove lines with #-
2. For files without these markers: Keep the code between Tabnine markers
"""

import os
import re
import shutil
import sys


def resolve_conflicts_in_file(file_path):
    print(f"Processing {file_path}...")

    # Create a backup
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Check if file contains Tabnine conflict markers
    pattern = r'<<<<<<< HEAD.*?=======.*?>>>>>>> Tabnine'#+
    if not re.search(pattern, content, re.DOTALL) and not ("#+" in content and "#-" in content):#+
        print(f"  No conflict markers found in {file_path}")
        return False

    # Case 1: Files with  and #- markers#-
    if "" in content and "#-" in content:#-
        # Keep lines with  and remove lines with #-#-
    # Case 1: Files with #+ and #- markers#+
    if "#+" in content and "#-" in content:#+
        # Keep lines with #+ and remove lines with #-#+
        lines = content.split('\n')
        new_lines = []
        in_conflict = False

        for line in lines:
            if "<<<<<<< HEAD" in line:#+
                in_conflict = True
                continue
            elif ">>>>>>> Tabnine" in line:#+
                in_conflict = False
                continue

            if in_conflict:
                if "#+" in line:  # Keep this line but remove the marker
                    new_lines.append(line.replace("#+", ""))
                elif "#-" not in line:  # Keep lines without markers
                    new_lines.append(line)
                # Skip lines with #-
            else:
                new_lines.append(line)

        new_content = '\n'.join(new_lines)

    # Case 2: Regular merge conflicts
    else:
        # Replace each conflict block with the Tabnine version
        new_content = re.sub(pattern, r'\1', content, flags=re.DOTALL)

        # Remove any remaining conflict markers
        new_content = re.sub(r'<<<<<<< HEAD.*?=======', '', new_content, flags=re.DOTALL)#+
        new_content = re.sub(r'>>>>>>> Tabnine', '', new_content)#+

    # Write the resolved content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  Resolved conflicts in {file_path}")
    return True


def main():
    # Find all files with Tabnine merge conflicts
    files_with_conflicts = []

    # Search for files with Tabnine merge conflicts
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        # Skip venv directory
        if 'venv' in dirs:
            dirs.remove('venv')
        # Skip .venv directory
        if '.venv' in dirs:
            dirs.remove('.venv')

        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.yml', '')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                        if re.search(r'<<<<<<< HEAD.*?=======.*?>>>>>>> Tabnine', content, re.DOTALL) or ("#+" in content and "#-" in content):#+
                            files_with_conflicts.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    if not files_with_conflicts:
        print("No files with Tabnine merge conflicts found.")
        return

    print(
        f"Found {len(files_with_conflicts)} files with Tabnine merge conflicts:")
    for file_path in files_with_conflicts:
        print(f"  {file_path}")

    # Resolve conflicts in each file
    resolved_count = 0
    for file_path in files_with_conflicts:
        if resolve_conflicts_in_file(file_path):
            resolved_count += 1

    print(
        f"\nResolved conflicts in {resolved_count} of {len(files_with_conflicts)} files.")
    print("\nNext steps:")
    print("  git add .")
    print("  git commit -m 'Resolve Tabnine merge conflicts'")
    print("  git push")


if __name__ == "__main__":
    main()
>>>>>>> Tabnine >>>>>>># {"source":"chat"}
