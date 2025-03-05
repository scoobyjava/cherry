console.log("Cherry project is running!");

// Simple application code
function main() {
  console.log("Welcome to Cherry - Code Analysis Tool");
  console.log("---------------------------------------");
  console.log("Available commands:");
  console.log("- npm start: Run the main application");
  console.log("- npm run analyze-complexity -- --file [filepath]: Analyze file complexity");
  console.log("- npm run sonar:start: Start SonarQube containers");
  console.log("- npm run sonar:stop: Stop SonarQube containers");
  console.log("- npm run sonar: Run SonarQube analysis");
}

main();