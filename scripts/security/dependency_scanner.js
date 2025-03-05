const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Dependency Scanner
 * Scans project dependencies for security vulnerabilities
 */
class DependencyScanner {
  constructor(config = {}) {
    this.config = {
      outputFormat: 'json',
      outputDir: './reports/dependency-scan',
      packageManager: 'npm',
      ignoreDevDependencies: false,
      severityThreshold: 'low',
      ...config
    };
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(this.config.outputDir)) {
      fs.mkdirSync(this.config.outputDir, { recursive: true });
    }
  }

  async scanNpmDependencies() {
    console.log('Scanning NPM dependencies for vulnerabilities...');
    
    try {
      const outputFile = path.join(this.config.outputDir, 'npm-audit-results.json');
      const command = `npm audit --json ${this.config.ignoreDevDependencies ? '--production' : ''} --audit-level=${this.config.severityThreshold}`;
      
      const output = execSync(command).toString();
      fs.writeFileSync(outputFile, output);
      
      return JSON.parse(output);
    } catch (error) {
      // npm audit returns non-zero exit code when vulnerabilities are found
      if (error.stdout) {
        const output = error.stdout.toString();
        const outputFile = path.join(this.config.outputDir, 'npm-audit-results.json');
        fs.writeFileSync(outputFile, output);
        
        return JSON.parse(output);
      }
      throw new Error(`Failed to scan NPM dependencies: ${error.message}`);
    }
  }
  
  async scanPythonDependencies() {
    console.log('Scanning Python dependencies for vulnerabilities...');
    
    try {
      const outputFile = path.join(this.config.outputDir, 'python-safety-results.json');
      const command = `safety check --json ${this.config.ignoreDevDependencies ? '--ignore-dev-dependencies' : ''}`;
      
      const output = execSync(command).toString();
      fs.writeFileSync(outputFile, output);
      
      return JSON.parse(output);
    } catch (error) {
      if (error.stdout) {
        const output = error.stdout.toString();
        const outputFile = path.join(this.config.outputDir, 'python-safety-results.json');
        fs.writeFileSync(outputFile, output);
        
        try {
          return JSON.parse(output);
        } catch (e) {
          return { error: "Could not parse safety output", raw: output };
        }
      }
      throw new Error(`Failed to scan Python dependencies: ${error.message}`);
    }
  }
  
  async scanAllDependencies() {
    const results = {
      timestamp: new Date().toISOString(),
      summary: { vulnerabilities: 0, packages: 0 },
      scans: {}
    };
    
    // Detect package managers based on files present
    if (fs.existsSync('package.json')) {
      try {
        const npmResults = await this.scanNpmDependencies();
        results.scans.npm = npmResults;
        
        if (npmResults.metadata) {
          results.summary.vulnerabilities += npmResults.metadata.vulnerabilities.total || 0;
          results.summary.packages += npmResults.metadata.totalDependencies || 0;
        }
      } catch (error) {
        results.scans.npm = { error: error.message };
      }
    }
    
    if (fs.existsSync('requirements.txt') || fs.existsSync('setup.py')) {
      try {
        const pythonResults = await this.scanPythonDependencies();
        results.scans.python = pythonResults;
        
        if (Array.isArray(pythonResults)) {
          results.summary.vulnerabilities += pythonResults.length;
          // Unique packages with vulnerabilities
          const vulnerablePackages = new Set(pythonResults.map(v => v[0]));
          results.summary.packages += vulnerablePackages.size;
        }
      } catch (error) {
        results.scans.python = { error: error.message };
      }
    }
    
    const summaryFile = path.join(this.config.outputDir, 'dependency-scan-summary.json');
    fs.writeFileSync(summaryFile, JSON.stringify(results, null, 2));
    
    return results;
  }
  
  formatResults(results) {
    const { summary, timestamp, scans } = results;
    
    let output = '# Dependency Scanning Results\n\n';
    output += `**Scan Date:** ${new Date(timestamp).toLocaleString()}\n\n`;
    output += `## Summary\n\n`;
    output += `- Total vulnerable packages found: ${summary.packages}\n`;
    output += `- Total vulnerabilities: ${summary.vulnerabilities}\n\n`;
    
    if (scans.npm) {
      output += `## NPM Dependencies\n\n`;
      if (scans.npm.error) {
        output += `Error scanning NPM dependencies: ${scans.npm.error}\n\n`;
      } else if (scans.npm.metadata) {
        const npmMeta = scans.npm.metadata;
        const vulns = npmMeta.vulnerabilities;
        
        output += `- Total dependencies: ${npmMeta.totalDependencies}\n`;
        output += `- Vulnerabilities: ${vulns.total} (Critical: ${vulns.critical}, High: ${vulns.high}, Moderate: ${vulns.moderate}, Low: ${vulns.low})\n\n`;
        
        if (vulns.total > 0 && scans.npm.advisories) {
          output += `### Vulnerabilities\n\n`;
          
          Object.values(scans.npm.advisories).forEach(adv => {
            output += `#### ${adv.title} (${adv.severity})\n\n`;
            output += `- Module: ${adv.module_name}\n`;
            output += `- Vulnerable versions: ${adv.vulnerable_versions}\n`;
            output += `- Patched versions: ${adv.patched_versions}\n`;
            output += `- Recommendation: ${adv.recommendation}\n\n`;
          });
        }
      }
    }
    
    if (scans.python) {
      output += `## Python Dependencies\n\n`;
      if (scans.python.error) {
        output += `Error scanning Python dependencies: ${scans.python.error}\n\n`;
      } else if (Array.isArray(scans.python)) {
        output += `- Vulnerabilities found: ${scans.python.length}\n\n`;
        
        if (scans.python.length > 0) {
          output += `### Vulnerabilities\n\n`;
          
          scans.python.forEach((vuln) => {
            // Safety output format: [package, installed_version, affected_versions, vulnerability_id, advisory]
            const [pkg, version, affected, id, advisory] = vuln;
            output += `#### ${pkg} (${version})\n\n`;
            output += `- Vulnerability ID: ${id}\n`;
            output += `- Affected versions: ${affected}\n`;
            output += `- Advisory: ${advisory}\n\n`;
          });
        }
      }
    }
    
    return output;
  }
}

module.exports = DependencyScanner;
