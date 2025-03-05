# SonarQube Integration

This project uses SonarQube for static code analysis to maintain code quality and identify potential issues.

## Setup

### Local Development

1. Start SonarQube server using Docker Compose:

```bash
docker-compose -f docker/sonarqube-docker-compose.yml up -d
```

2. Access SonarQube at http://localhost:9000 (default credentials: admin/admin)

3. Create a project and generate a token

4. Run analysis locally:

```bash
npx sonar-scanner \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_GENERATED_TOKEN
```

### CI Pipeline

The GitHub Actions workflow automatically runs SonarQube analysis on pull requests and pushes to main.

## Configuration

- Project settings are defined in `sonar-project.properties`
- Quality gates and advanced settings can be configured in the SonarQube UI

## Quality Gates

The project is configured to maintain:
- Code coverage > 80%
- Fewer than 5 critical issues
- No security hotspots

## Reports

SonarQube reports can be accessed via the SonarQube UI or through the CI pipeline artifacts.
