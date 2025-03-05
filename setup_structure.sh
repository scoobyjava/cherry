#!/bin/bash

# Create main directories
mkdir -p src/components
mkdir -p src/utils
mkdir -p src/styles
mkdir -p src/assets
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p docs/api
mkdir -p docs/guides

# Create basic README
cat > README.md << 'EOL'
# Cherry Project

A well-organized project structure with clear separation of concerns.

## Directory Structure

- `src/` - Main source code
  - `components/` - Reusable UI components
  - `utils/` - Helper functions and utilities
  - `styles/` - CSS and styling files
  - `assets/` - Images, fonts, and other static assets
- `tests/` - Test suites
  - `unit/` - Unit tests
  - `integration/` - Integration tests
- `docs/` - Documentation
  - `api/` - API documentation
  - `guides/` - User and developer guides

## Getting Started

[Instructions on how to set up and run the project]
EOL

# Create basic files in each directory to prevent empty directories in git
touch src/components/.gitkeep
touch src/utils/.gitkeep
touch src/styles/.gitkeep
touch src/assets/.gitkeep
touch tests/unit/.gitkeep
touch tests/integration/.gitkeep
touch docs/api/.gitkeep
touch docs/guides/.gitkeep

# Create a basic .gitignore file
cat > .gitignore << 'EOL'
# Dependency directories
node_modules/
vendor/

# Build outputs
dist/
build/
out/

# Environment files
.env
.env.local
.env.*.local

# Log files
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Editor directories and files
.idea/
.vscode/*
!.vscode/extensions.json
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
EOL

echo "Repository structure created successfully!"
