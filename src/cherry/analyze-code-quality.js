const fs = require('fs');

function standardizeIssues(rawIssues, sourcePath, issueType) {
  // Convert raw issues into a common schema:
  // { filePath, type, description, severity, snippet }
  return rawIssues.map(issue => ({
    filePath: sourcePath,
    type: issueType,
    description: issue.description || "Issue detected",
    severity: issue.severity || "medium",
    snippet: issue.snippet || ""
  }));
}

// Example: Assuming sonarPrioritized results contain an array of raw issues
const rawSonarIssues = JSON.parse(fs.readFileSync('sonar-prioritized.json', 'utf8'));
// Transform them into standardized issues
const qualityIssues = standardizeIssues(rawSonarIssues, "path/to/analyzed/file.js", "quality_issue");

// Write out standardized issues for quality analysis (you might write on a per-file basis)
fs.writeFileSync('quality_issues.json', JSON.stringify(qualityIssues, null, 2), 'utf8');
