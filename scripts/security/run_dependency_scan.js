const path = require('path');
const fs = require('fs');
const DependencyScanner = require('./dependency_scanner');

async function loadConfig() {
  try {
    const configPath = path.resolve(process.cwd(), 'benchmarks/benchmark_config.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    
    // Extract security scanning configuration if it exists
    if (config.security_scanning && config.security_scanning.dependency_scan) {
      return config.security_scanning.dependency_scan;
    }
    return {};
  } catch (error) {
    console.warn('Could not load security scanning config:', error.message);
    return {};
  }
}

async function main() {
  try {
    console.log('=== Dependency Vulnerability Scanner ===');
    
    const config = await loadConfig();
    const scanner = new DependencyScanner(config);
    
    console.log('Starting dependency scan...');
    const results = await scanner.scanAllDependencies();
    
    console.log('\n=== Scan Complete ===');
    console.log(`Found ${results.summary.vulnerabilities} vulnerabilities in ${results.summary.packages} packages.`);
    
    // Generate a formatted report
    const formattedResults = scanner.formatResults(results);
    
    // Save formatted report to file
    const reportPath = path.join(scanner.config.outputDir, 'dependency-scan-report.md');
    fs.writeFileSync(reportPath, formattedResults);
    
    console.log(`\nDetailed report saved to ${reportPath}`);
    console.log('\n=== Dependency Scan Results ===\n');
    console.log(formattedResults);
    
    // Exit with error code if vulnerabilities were found
    if (results.summary.vulnerabilities > 0) {
      process.exit(1);
    }
  } catch (error) {
    console.error('Error running dependency scan:', error);
    process.exit(1);
  }
}

// Run the scan
main();
