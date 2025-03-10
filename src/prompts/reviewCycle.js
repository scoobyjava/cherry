/**
 * Structured prompts for the ReviewerAgent and Copilot interaction
 */
module.exports = {
  // ReviewerAgent initial analysis prompt
  codeReview: (code, context) => `
    Analyze the following code in the context of ${context.project || "the Cherry AI System"}:
    
    \`\`\`
    ${code}
    \`\`\`
    
    Generate a structured review with the following sections:
    1. Functionality: Does the code correctly implement its intended purpose?
    2. Performance: Identify potential bottlenecks or optimization opportunities
    3. Code Quality: Evaluate patterns, readability, and maintainability
    4. Security: Highlight any security concerns or vulnerabilities
    5. Testing Coverage: Areas that need better test coverage
    
    For each section, assign a priority level (P0-Critical, P1-High, P2-Medium, P3-Low)
    and provide specific, actionable recommendations.
  `,
  
  // Copilot improvement prompt
  generateImprovements: (code, review) => `
    Improve the following code based on the review feedback:
    
    CODE:
    \`\`\`
    ${code}
    \`\`\`
    
    REVIEW:
    ${JSON.stringify(review, null, 2)}
    
    Implement all P0-Critical and P1-High priority changes.
    For P2-Medium issues, implement those related to performance and security.
    For P3-Low issues, include TODO comments where appropriate.
    
    Provide an explanation of your changes and their expected impact.
  `,
  
  // ReviewerAgent validation prompt
  validateImprovements: (originalCode, improvedCode, originalReview) => `
    Compare the original code:
    \`\`\`
    ${originalCode}
    \`\`\`
    
    With the improved code:
    \`\`\`
    ${improvedCode}
    \`\`\`
    
    Original review:
    ${JSON.stringify(originalReview, null, 2)}
    
    Evaluate how well the improvements address the issues from the original review.
    For each issue in the original review, determine if it was:
    - Fully addressed
    - Partially addressed
    - Not addressed
    
    Also identify any new issues introduced.
    Provide a quantitative improvement score (0-100%).
  `,
  
  // User feedback integration prompt
  incorporateFeedback: (code, improvements, feedback) => `
    The following code:
    \`\`\`
    ${code}
    \`\`\`
    
    Has been improved to:
    \`\`\`
    ${improvements}
    \`\`\`
    
    User feedback:
    ${feedback}
    
    Refine the improved code to specifically address the user feedback while preserving
    the technical improvements. Provide explanations for your changes.
  `,
  
  // Test results integration prompt
  addressTestFailures: (code, testResults) => `
    The following code:
    \`\`\`
    ${code}
    \`\`\`
    
    Failed these tests:
    ${JSON.stringify(testResults.failures, null, 2)}
    
    Modify the code to fix the failing tests while maintaining code quality.
    Explain your approach to fixing each test failure.
  `
};