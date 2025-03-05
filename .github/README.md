# Cherry Project Code Quality & Security

This project uses a comprehensive code scanning setup to ensure code quality and security:

## Security & Quality Scanning Tools

### CodeQL
- Analyzes code for security vulnerabilities and coding errors
- Supports JavaScript, TypeScript, and Python
- Runs automatically on PRs and scheduled scans

### SonarQube
- Provides static code analysis for code quality and security issues
- Enforces quality gates before merges
- Configuration defined in `benchmarks/benchmark_config.json`

### Checkov
- Scans Infrastructure as Code (IaC) files for security issues
- Covers Terraform, CloudFormation, Kubernetes, Dockerfiles, and Helm
- Uses baseline configuration in `security/checkov_baseline.json`

## Workflow

The GitHub Actions workflow in `.github/workflows/code-quality.yml` runs these tools:
- On every pull request to main/master
- On every push to main/master
- On a weekly schedule (Monday 4 AM UTC)

## Configuration

- SonarQube and Checkov configurations are loaded from the benchmark_config.json file
- Security scan results are uploaded as artifacts for review
- Failed security checks will block merges to protected branches
