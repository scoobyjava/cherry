# GitHub Organizational Secrets Guide

## Overview

We've moved from Azure Key Vault and repository-level secrets to GitHub organizational secrets for managing sensitive information. This document explains how to set up and use GitHub organizational secrets in this project.

## Setting Up GitHub Organizational Secrets

1. Go to your GitHub organization's page
2. Click on **Settings**
3. In the left sidebar, select **Secrets and variables** then **Actions**
4. Click on **New organization secret**
5. For each key, enter a name and paste the corresponding value
6. Under **Repository access**, you can choose:
   - **All repositories** - Makes the secret available to all repositories in the organization
   - **Selected repositories** - Allows you to choose specific repositories that can access the secret

## Required Organizational Secrets

Set up the following secrets in your GitHub organization:

- `AZURE_STORAGE_ACCOUNT`: Your Azure Storage account name
- `AZURE_STORAGE_KEY`: Your storage access key
- `AZURE_STORAGE_CONNECTION_STRING`: Your Azure Storage connection string
- `PHOENIX_API_KEY`: Your Phoenix monitoring API key
- `MY_SECRET`: Any other application-specific secrets

## Accessing Organizational Secrets

### In GitHub Actions Workflows

Organizational secrets are automatically available as environment variables in GitHub Actions workflows for repositories that have access to them:

```yaml
<<<<<<< Tabnine <<<<<<<
# No//-
```//-
import os//+
//+
# Get a secret value//+
secret_value = os.environ.get("MY_SECRET")//+
if secret_value://+
    print("Secret retrieved successfully")//+
else://+
    print("Secret not found")//+
>>>>>>> Tabnine >>>>>>>// {"source":"chat"}
