const fs = require('fs');

// Load analysis results
const sourcegraphResults = JSON.parse(fs.readFileSync('sourcegraph-results.json', 'utf8'));
const sonarPrioritized = JSON.parse(fs.readFileSync('sonar-prioritized.json', 'utf8'));

// Generate recommendations
const recommendations = [];

if (sourcegraphResults.errorHandlingOpportunities > 0) {
  recommendations.push("Standardize error handling patterns");
}

if (sourcegraphResults.potentialDuplication > 0) {
  recommendations.push("Consolidate duplicate utility functions");
}

if (sonarPrioritized.criticalIssues.length > 0) {
  recommendations.push("Address critical security vulnerabilities");
}

// Create a summary
const summary = {
  securityIssues: sonarPrioritized.criticalIssues.length,
  performanceIssues: sonarPrioritized.quickWins.length,
  maintainabilityScore: 85, // Example - replace with actual calculation
  recommendations,
  reportUrl: "https://sonarcloud.io/dashboard?id=cherry"
};

// Write the summary
fs.writeFileSync('cherry-analysis-summary.json', JSON.stringify(summary, null, 2));
console.log("Cherry analysis complete:", summary);
