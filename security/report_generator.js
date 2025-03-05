const fs = require('fs');
const path = require('path');

/**
 * Generate a detailed vulnerability report
 * @param {Object} scanResults - Results from dependency scans
 * @param {string} outputPath - Path to save the report
 */
function generateReport(scanResults, outputPath) {
  const timestamp = new Date().toISOString();
  const report = {
    timestamp,
    summary: summarizeVulnerabilities(scanResults),
    details: scanResults,
    recommendations: generateRecommendations(scanResults)
  };

  // Create HTML report
  const htmlReport = generateHtmlReport(report);
  fs.writeFileSync(path.join(outputPath, 'vulnerability_report.html'), htmlReport);

  // Create JSON report
  fs.writeFileSync(
    path.join(outputPath, 'vulnerability_report.json'), 
    JSON.stringify(report, null, 2)
  );

  console.log(`Reports generated at ${outputPath}`);
}

/**
 * Summarize vulnerabilities by severity
 * @param {Object} scanResults - Results from dependency scans
 * @returns {Object} - Summary of vulnerabilities
 */
function summarizeVulnerabilities(scanResults) {
  const summary = {
    total: 0,
    critical: 0,
    high: 0,
    moderate: 0,
    low: 0,
    info: 0,
    projects: {}
  };

  for (const [projectPath, result] of Object.entries(scanResults)) {
    if (result.error) continue;
    
    const projectName = path.basename(projectPath);
    summary.projects[projectName] = { total: 0, critical: 0, high: 0, moderate: 0, low: 0, info: 0 };
    
    // For npm audit format
    if (result.metadata && result.vulnerabilities) {
      Object.values(result.vulnerabilities).forEach(vuln => {
        summary.total++;
        summary.projects[projectName].total++;
        
        summary[vuln.severity.toLowerCase()]++;
        summary.projects[projectName][vuln.severity.toLowerCase()]++;
      });
    }
    
    // For Python safety format
    if (Array.isArray(result)) {
      result.forEach(vuln => {
        summary.total++;
        summary.projects[projectName].total++;
        
        // Map safety severity to our categories
        const severity = mapPythonSeverity(vuln.severity);
        summary[severity]++;
        summary.projects[projectName][severity]++;
      });
    }
  }
  
  return summary;
}

/**
 * Map Python safety severity to standard categories
 * @param {string} severity - Safety severity string
 * @returns {string} - Mapped severity category
 */
function mapPythonSeverity(severity) {
  // Safety uses a different severity scale, mapping to our categories
  const severityMap = {
    'critical': 'critical',
    'high': 'high',
    'medium': 'moderate',
    'low': 'low',
    'info': 'info'
  };
  
  return severityMap[severity.toLowerCase()] || 'info';
}

/**
 * Generate recommended actions based on scan results
 * @param {Object} scanResults - Results from dependency scans
 * @returns {Array} - List of recommendations
 */
function generateRecommendations(scanResults) {
  const recommendations = [];
  
  for (const [projectPath, result] of Object.entries(scanResults)) {
    if (result.error) {
      recommendations.push({
        project: path.basename(projectPath),
        action: 'Run manual scan',
        reason: `Automated scan failed: ${result.error}`,
        priority: 'Medium'
      });
      continue;
    }
    
    // For npm audit format
    if (result.metadata && result.vulnerabilities) {
      Object.entries(result.vulnerabilities).forEach(([pkgName, vuln]) => {
        if (vuln.severity === 'critical' || vuln.severity === 'high') {
          recommendations.push({
            project: path.basename(projectPath),
            action: `Update ${pkgName} to ${vuln.fixAvailable?.version || 'latest version'}`,
            reason: `${vuln.severity.toUpperCase()} severity vulnerability: ${vuln.title}`,
            priority: vuln.severity === 'critical' ? 'Critical' : 'High',
            cve: vuln.cves?.[0] || 'N/A'
          });
        }
      });
    }
    
    // For Python safety format
    if (Array.isArray(result)) {
      result.forEach(vuln => {
        if (['critical', 'high'].includes(vuln.severity.toLowerCase())) {
          recommendations.push({
            project: path.basename(projectPath),
            action: `Update ${vuln.package_name} to ${vuln.fixed_version || 'latest version'}`,
            reason: `${vuln.severity.toUpperCase()} severity vulnerability: ${vuln.advisory}`,
            priority: vuln.severity.toLowerCase() === 'critical' ? 'Critical' : 'High',
            cve: vuln.cve || 'N/A'
          });
        }
      });
    }
  }
  
  // Sort recommendations by priority
  const priorityOrder = { 'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3 };
  recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
  
  return recommendations;
}

/**
 * Generate an HTML report
 * @param {Object} report - Vulnerability report data
 * @returns {string} - HTML content
 */
function generateHtmlReport(report)