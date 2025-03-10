/**
 * Structured prompts for agent interaction in review cycles
 */
module.exports = {
  // Initial code review prompt
  initialReview: (code, context) => `
    Analyze the following code:
    \`\`\`
    ${code}
    \`\`\`
    
    Context: ${context}
    
    Provide a structured review focusing on:
    1. Correctness: Is the implementation correct?
    2. Performance: Identify potential bottlenecks
    3. Security: Highlight security concerns
    4. Maintainability: Evaluate code organization
    
    Format your response as a JSON object with sections for each concern and severity levels.
  `,
  
  // Prompt for iterative improvements
  improvementRequest: (review, previousCode) => `
    Based on the following review:
    ${JSON.stringify(review, null, 2)}
    
    Improve this code:
    \`\`\`
    ${previousCode}
    \`\`\`
    
    Focus on addressing the concerns with severity levels "high" and "medium" first.
    Provide explanations for your changes.
  `,
  
  // Validation prompt
  validateChanges: (originalCode, improvedCode, review) => `
    Compare the original code:
    \`\`\`
    ${originalCode}
    \`\`\`
    
    With the improved version:
    \`\`\`
    ${improvedCode}
    \`\`\`
    
    Verify that the improvements address these concerns:
    ${JSON.stringify(review.concerns, null, 2)}
    
    Return a validation report with:
    1. Whether each concern was addressed (yes/no/partial)
    2. Any new concerns introduced
    3. Overall improvement assessment (1-10)
  `
};
