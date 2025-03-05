#!/usr/bin/env node

const path = require('path');
const fs = require('fs');
const DependencyAnalyzer = require('../utils/dependency-analyzer');

// Configure output directory
const OUTPUT_DIR = path.join(__dirname, '../reports/dependencies');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function main() {
  try {
    // Project root directory (adjust if needed)
    const rootDir = path.join(__dirname, '..');
    
    console.log('Analyzing dependencies...');
    const analyzer = new DependencyAnalyzer(rootDir);
    
    // Scan the project
    await analyzer.scan();
    
    // Generate report
    const report = analyzer.generateReport();
    
    // Export dependency graph for visualization
    const graph = analyzer.exportDependencyGraph();
    
    // Output results
    console.log(`\nAnalysis complete!`);
    console.log(`Found ${report.totalModules} modules with ${report.circularDependencyCount} circular dependencies.\n`);
    
    if (report.circularDependencies.length > 0) {
      console.log('Circular Dependencies:');
      report.circularDependencies.forEach((cycle, i) => {
        console.log(`${i + 1}. ${cycle.join(' -> ')} -> ${cycle[0]}`);
      });
    }
    
    // Save reports to files
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'dependency-report.json'), 
      JSON.stringify(report, null, 2)
    );
    
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'dependency-graph.json'), 
      JSON.stringify(graph, null, 2)
    );
    
    // Generate HTML visualization
    generateHtmlVisualization(graph);
    
    console.log(`\nReports saved to ${OUTPUT_DIR}`);
  } catch (error) {
    console.error('Error analyzing dependencies:', error);
    process.exit(1);
  }
}

function generateHtmlVisualization(graph) {
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Dependency Graph Visualization</title>
  <meta charset="utf-8">
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; }
    #graph { width: 100vw; height: 100vh; }
    .node { cursor: pointer; }
    .link { stroke: #999; stroke-opacity: 0.6; }
    .circular { stroke: red; stroke-width: 3px; }
    
    .tooltip {
      position: absolute;
      background-color: white;
      padding: 5px;
      border: 1px solid #ddd;
      border-radius: 5px;
      pointer-events: none;
      font-size: 12px;
    }
    
    .controls {
      position: absolute;
      top: 10px;
      left: 10px;
      background-color: rgba(255, 255, 255, 0.8);
      padding: 10px;
      border-radius: 5px;
    }
  </style>
</head>
<body>
  <div class="controls">
    <h3>Module Dependencies</h3>
    <div>
      <label>
        <input type="checkbox" id="highlightCircular" checked>
        Highlight circular dependencies
      </label>
    </div>
    <div id="stats"></div>
  </div>
  <div id="graph"></div>
  
  <script>
    // Load the graph data
    const graph = ${JSON.stringify(graph)};
    
    const width = window.innerWidth;