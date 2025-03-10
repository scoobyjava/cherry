#!/usr/bin/env python3
import os
import json
import yaml


class RepoHealthChecker:
    def __init__(self):
        self.repo_root = os.getcwd()
        self.essential_files = [
            'README.md',
            'LICENSE',
            '.gitignore',
            'CONTRIBUTING.md',
            'CODE_OF_CONDUCT.md',
            '.github/ISSUE_TEMPLATE/bug_report.md',
            '.github/ISSUE_TEMPLATE/feature_request.md',
            '.github/dependabot.yml',
            '.github/workflows/ci.yml',
            'package.json',
        ]

    def check_health(self):
        """Run a comprehensive health check on the repository"""
        print("🔍 Running repository health check...")

        self._check_essential_files()
        self._check_github_templates()
        self._check_security_files()
        self._check_npm_config()

        print("✅ Health check complete!")

    def _check_essential_files(self):
        """Check if all essential files exist"""
        print("\n📁 Checking essential files:")
        for file in self.essential_files:
            path = os.path.join(self.repo_root, file)
            exists = os.path.exists(path)
            status = "✅" if exists else "❌"
            print(f"{status} {file}")

    def _check_github_templates(self):
        """Check GitHub templates"""
        print("\n📋 Checking GitHub templates:")
        template_dir = os.path.join(self.repo_root, '.github')

        if not os.path.exists(template_dir):
            print("❌ Missing .github directory")
            return

        # Check PR template
        pr_template = os.path.join(template_dir, 'PULL_REQUEST_TEMPLATE.md')
        if (os.path.exists(pr_template)):
            print("✅ Pull request template exists")
        else:
            print("❌ Missing pull request template")

    def _check_security_files(self):
        """Check security-related files"""
        print("\n🔒 Checking security files:")
        security_file = os.path.join(self.repo_root, 'SECURITY.md')
        if os.path.exists(security_file):
            print("✅ SECURITY.md exists")
        else:
            print("❌ Missing SECURITY.md")

    def _check_npm_config(self):
        """Check npm configuration"""
        print("\n📦 Checking npm configuration:")
        package_json = os.path.join(self.repo_root, 'package.json')

        if not os.path.exists(package_json):
            print("❌ No package.json found")
            return

        with open(package_json, 'r') as f:
            try:
                pkg = json.load(f)

                if 'scripts' in pkg and 'test' in pkg['scripts']:
                    print("✅ Test script defined")
                else:
                    print("❌ Missing test script")

                if 'repository' in pkg:
                    print("✅ Repository field defined")
                else:
                    print("❌ Missing repository field")

                if 'engines' in pkg:
                    print("✅ Node.js engine constraints defined")
                else:
                    print("❌ Missing Node.js engine constraints")

            except json.JSONDecodeError:
                print("❌ Invalid package.json format")


if __name__ == "__main__":
    checker = RepoHealthChecker()
    checker.check_health()
