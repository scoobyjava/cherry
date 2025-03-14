# Secrets Management Guide

## Using GitHub Secrets

We've moved from Azure Key Vault to GitHub Secrets for managing sensitive information. This document explains how to set up and use GitHub Secrets in this project.

### Setting Up GitHub Secrets

1. Go to your GitHub repository's page
2. Click on the **Settings** tab
3. In the left sidebar, select **Secrets and variables** then **Actions**
4. Click on **New repository secret**
5. For each key, enter a name and paste the corresponding value

### Required Secrets

Set up the following secrets in your GitHub repository:

- `AZURE_STORAGE_ACCOUNT`: Your Azure Storage account name
- `AZURE_STORAGE_KEY1`: Your primary storage access key
- `AZURE_STORAGE_CONNECTION_STRING`: Your Azure Storage connection string
- `PHOENIX_API_KEY`: Your Phoenix monitoring API key
- `MY_SECRET`: Any other application-specific secrets

### Accessing Secrets

#### In GitHub Actions Workflows

Secrets are automatically available as environment variables in GitHub Actions:

```yaml
env:
  MY_SECRET: ${{ secrets.MY_SECRET }}
```
