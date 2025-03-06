# Setting Up GitHub Integration for Cherry

This guide will help you connect your local Cherry repository to GitHub and push your code.

## Prerequisites

- A GitHub account
- Git installed on your local machine
- A Cherry repository already initialized locally
- A GitHub repository created for your project

## Linking Your Local Repository to GitHub

1. Navigate to your Cherry repository in the terminal:

```bash
cd /path/to/your/cherry
```

2. Add the GitHub repository as a remote origin:

```bash
git remote add origin <REPO_URL>
```

Replace `<REPO_URL>` with the URL of your GitHub repository, which should look like:

- HTTPS: `https://github.com/username/cherry.git`
- SSH: `git@github.com:username/cherry.git`

3. Verify that the remote was added correctly:

```bash
git remote -v
```

This should display the remote URL for fetch and push operations.

## Pushing Your Code to GitHub

1. Make sure all your changes are committed locally:

```bash
git status
git add .
git commit -m "Initial commit"
```

2. Push your code to the GitHub repository:

```bash
git push -u origin main
```

Note: If your default branch is named differently (e.g., "master" instead of "main"), replace "main" with your branch name.

The `-u` flag sets up tracking, which means you can run `git push` and `git pull` in the future without specifying the remote and branch.

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

- For HTTPS URLs: You might be prompted for your GitHub username and password. If you have 2FA enabled, you'll need to use a personal access token instead of your password.
- For SSH URLs: Make sure your SSH key is added to your GitHub account and your SSH agent.

### Branch Name Issues

If you get an error about the branch not existing:

```bash
git push -u origin main:main
```

This explicitly creates the "main" branch on the remote if it doesn't exist.

### Default Branch Is Not "main"

If your local repository's default branch is not "main" (e.g., it's "master"), you can:

```bash
# Option 1: Push to master
git push -u origin master

# Option 2: Rename master to main locally and then push
git branch -M main
git push -u origin main
```

## Next Steps

After successfully pushing your code to GitHub, you might want to:

1. Set up GitHub Actions for continuous integration
2. Create a README.md file to explain your project
3. Add a LICENSE file to specify the license for your project
4. Configure branch protection rules

## Cherry AI Environment Configuration

To set up the Cherry AI environment, create a `devcontainer.json` file with the following content:

```json
{
  "name": "Cherry AI Environment",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:20",
  "forwardPorts": [8000, 9000, 3000],
  "portsAttributes": {
    "8000": {
      "label": "Cherry API",
      "onAutoForward": "openBrowser",
      "visibility": "public"
    },
    "9000": {
      "label": "SonarQube",
      "onAutoForward": "notify",
      "visibility": "public"
    },
    "3000": {
      "label": "Next.js Dev",
      "onAutoForward": "openBrowser",
      "visibility": "public"
    }
  },
  "hostRequirements": {
    "cpus": 4,
    "memory": "8gb",
    "storage": "32gb"
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-azuretools.vscode-docker",
        "ms-python.python",
        "github.copilot",
        "github.copilot-chat",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "ms-python.vscode-pylance",
        "njpwerner.autodocstring",
        "sourcegraph.cody",
        "sonarsource.sonarlint-vscode",
        "bradlc.vscode-tailwindcss",
        "dsznajder.es7-react-js-snippets",
        "eamodio.gitlens",
        "mtxr.sqltools",
        "github.vscode-github-actions",
        "github.vscode-pull-request-github",
        "csstools.postcss",
        "wix.vscode-import-cost",
        "VisualStudioExptTeam.vscodeintellicode"
      ],
      "settings": {
        "github.copilot.enable": {
          "*": true
        },
        "github.copilot.advanced": {
          "codeReferencing": "warning",
          "model": "gpt-4o",
          "temperature": 0.2,
          "confidential": {
            "enableFiltering": false
          }
        },
        "sourcegraph.url": "https://cherry-ai.sourcegraph.app",
        "sourcegraph.experimentalFeatures": {
          "cody": true
        },
        "sonarlint.connectedMode.project": {
          "projectKey": "cherry"
        },
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "editor.inlineSuggest.enabled": true,
        "editor.inlineSuggest.showToolbar": "onHover",
        "javascript.updateImportsOnFileMove.enabled": "always",
        "typescript.updateImportsOnFileMove.enabled": "always",
        "editor.codeActionsOnSave": {
          "source.fixAll.eslint": true,
          "source.organizeImports": true
        },
        "jest.autoRun": "off",
        "tailwindCSS.includeLanguages": {
          "javascript": "javascript",
          "typescript": "typescript",
          "javascriptreact": "javascriptreact",
          "typescriptreact": "typescriptreact"
        }
      }
    },
    "github.com": {
      "copilot": {
        "enabled": true
      }
    }
  },
  "features": {
    "python": "3.10",
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    },
    "ghcr.io/devcontainers-contrib/features/jest:2": {},
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers-contrib/features/pnpm:2": {},
    "ghcr.io/devcontainers-contrib/features/typescript:2": {}
  },
  "initializeCommand": "mkdir -p .vscode",
  "postCreateCommand": "npm install && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && pip install pylint pytest && npm install -g madge && git config --global pull.rebase true",
  "postStartCommand": "echo 'Creating Sourcegraph and SonarLint config...' && mkdir -p /workspaces/cherry/.vscode && echo '{\"sourcegraph.url\": \"https://cherry-ai.sourcegraph.app\", \"sonarlint.connectedMode.project\": {\"projectKey\": \"cherry\"}}' > /workspaces/cherry/.vscode/settings.json"
}
```
