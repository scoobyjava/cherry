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
