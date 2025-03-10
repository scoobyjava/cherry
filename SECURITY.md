# Security Policy

## Supported Versions

We currently support the following versions of the Cherry project with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Cherry seriously. If you believe you've found a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** disclose the vulnerability publicly on GitHub Issues, Discord, or any public channels.
2. Email your findings to [security@example.com](mailto:security@example.com). If possible, encrypt your message with our [PGP key](#pgp-key).
3. Include as much information as possible:
   - A description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fixes (if any)

### What to Expect

- You'll receive an acknowledgment of your report within 48 hours.
- We'll investigate and provide a timeline for a fix (typically within 7 days).
- We'll keep you updated as we work on the fix.
- After the issue is resolved, we'll publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous).

## Security Measures

This project implements several security measures:

1. **Automated Dependency Scanning**: We use Dependabot to scan for vulnerable dependencies and automatically create pull requests to update them.

2. **Static Code Analysis**: Our codebase is regularly scanned with CodeQL to identify potential security issues.

3. **Regular Updates**: We maintain regular updates to all dependencies to ensure security patches are applied promptly.

## Best Practices

When contributing to this project, please follow these security best practices:

1. Keep all dependencies updated to their latest secure versions.
2. Do not commit sensitive information such as API keys, passwords, or personal data.
3. Follow the principle of least privilege in all code contributions.
4. Use parameterized queries and input validation to prevent injection attacks.
5. Validate and sanitize all user inputs.

## PGP Key

For encrypted communications, you can use our public PGP key:

```
[Insert your PGP key here if applicable]
```

## Security Updates

Security updates will be released as part of our regular version updates. Critical vulnerabilities may receive expedited patches outside the normal release cycle.

## CodeRabbit Code Review

```yaml
name: CodeRabbit Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  coderabbit-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: coderabbitai/coderabbit@v0.14.0
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
````

## Implementation Instructions

1. Create a SECURITY.md file in the root of your repository:

```bash
touch SECURITY.md
```

2. Copy the content provided above into the file.

3. Customize the following sections:
   - Update the email address (currently `security@example.com`)
   - Add your PGP key if you have one
   - Adjust the supported versions based on your actual versioning scheme
   - Modify any specific security measures that might be different in your project

4. Commit and push the file to your repository:

```bash
git add SECURITY.md
git commit -m "Add security policy"
git push origin main
