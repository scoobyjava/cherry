#!/usr/bin/env python3
import os
import json
import subprocess
import re


class NPMConfigHelper:
    def __init__(self):
        self.package_json = 'package.json'
        self.npmrc = '.npmrc'

    def setup_publishing(self):
        """Set up npm publishing configuration"""
        if not os.path.exists(self.package_json):
            print("❌ No package.json found")
            return

        # Check if user is logged in to npm
        try:
            whoami = subprocess.run(['npm', 'whoami'],
                                    capture_output=True,
                                    text=True)

            if whoami.returncode != 0:
                print("❌ Not logged in to npm. Run 'npm login' first.")
                return

            username = whoami.stdout.strip()
            print(f"✅ Logged in as {username}")

            # Update package.json
            with open(self.package_json, 'r') as f:
                pkg = json.load(f)

            # Add publishConfig if not present
            if 'publishConfig' not in pkg:
                pkg['publishConfig'] = {
                    'access': 'public'
                }
                print("✅ Added publishConfig to package.json")

            # Add author if not present
            if 'author' not in pkg:
                pkg['author'] = {
                    'name': username,
                    'url': f'https://www.npmjs.com/~{username}'
                }
                print("✅ Added author information to package.json")

            # Save updated package.json
            with open(self.package_json, 'w') as f:
                json.dump(pkg, f, indent=2)

            # Create or update .npmrc file
            npmrc_content = "save-exact=true\npackage-lock=true\n"

            with open(self.npmrc, 'w') as f:
                f.write(npmrc_content)
            print("✅ Created .npmrc file")

            print("\n📋 Instructions for setting up GitHub Actions:")
            print("1. Generate an npm token with: npm token create")
            print(
                "2. Add the token as a secret named NPM_TOKEN in your GitHub repository")
            print("3. Use this token in your GitHub Actions workflow")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    helper = NPMConfigHelper()
    helper.setup_publishing()
