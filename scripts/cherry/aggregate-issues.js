const fs = require('fs');

function loadIssues(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    return [];
  }
}

const securityIssues = loadIssues('security_issues.json');  // Issues output by developer.py
const qualityIssues = loadIssues('quality_issues.json');      // Issues output by analyze-code-quality.js

// Merge issues arrays
const allIssues = [...securityIssues, ...qualityIssues];

// Write the aggregated issues to a central JSON file
fs.writeFileSync('analysis_issues.json', JSON.stringify(allIssues, null, 2), 'utf8');
