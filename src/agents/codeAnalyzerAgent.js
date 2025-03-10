const logger = require("../utils/unifiedLogger");
const { query } = require("../integrations/huggingfaceClient");
const memorySystem = require("../memory/memorySystem");

class CodeAnalyzerAgent {
  constructor() {
    this.codeModel = "Salesforce/codet5p-220m"; // Code-specific model
    this.summaryModel = "sshleifer/distilbart-cnn-12-6";
  }

  async execute(params) {
    const { action, payload, memoryId } = params;

    switch (action) {
      case "analyze_changes":
        return await this.analyzeChanges(payload, memoryId);
      case "code_review":
        return await this.reviewCode(payload);
      case "generate_tests":
        return await this.generateTests(payload);
      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }

  async analyzeChanges(payload, memoryId) {
    logger.info("Analyzing code changes", {
      repository: payload.repository?.full_name,
    });

    try {
      // Get the files changed in this push
      const changedFiles = new Set();
      payload.commits.forEach((commit) => {
        commit.added?.forEach((file) => changedFiles.add(file));
        commit.modified?.forEach((file) => changedFiles.add(file));
      });

      const results = {
        changedFiles: Array.from(changedFiles),
        analysis: {},
        summary: "",
        qualityIssues: [],
      };

      // For demo purposes, let's analyze up to 3 files
      const filesToAnalyze = Array.from(changedFiles).slice(0, 3);

      for (const file of filesToAnalyze) {
        // In a real implementation, we would fetch the file content from GitHub API
        // For now, we'll simulate with a placeholder
        const fileExtension = file.split(".").pop();
        if (
          ["js", "ts", "py", "java", "c", "cpp", "cs"].includes(fileExtension)
        ) {
          const fileAnalysis = await this.analyzeFile(
            file,
            'console.log("Example code")'
          );
          results.analysis[file] = fileAnalysis;

          if (fileAnalysis.qualityIssues?.length > 0) {
            results.qualityIssues.push(
              ...fileAnalysis.qualityIssues.map((issue) => ({
                file,
                ...issue,
              }))
            );
          }
        }
      }

      // Generate overall summary
      const commitMessages = payload.commits
        .map((commit) => commit.message)
        .join(". ");
      results.summary = await query(this.summaryModel, {
        inputs: `Changes to ${results.changedFiles.length} files. ${commitMessages}`,
        parameters: {
          max_length: 100,
          min_length: 30,
        },
      });

      // Store analysis results in memory
      await memorySystem.store("semantic", `code_analysis_${payload.after}`, {
        type: "code_analysis",
        repository: payload.repository.full_name,
        branch: payload.ref,
        results,
        timestamp: new Date().toISOString(),
      });

      // Connect this analysis to the original webhook event
      if (memoryId) {
        await memorySystem.update("episodic", memoryId, {
          codeAnalysisComplete: true,
          qualityIssuesFound: results.qualityIssues.length,
        });
      }

      logger.info("Code analysis complete", {
        repository: payload.repository.full_name,
        issuesFound: results.qualityIssues.length,
      });

      return {
        success: true,
        message: `Analyzed ${results.changedFiles.length} files`,
        issuesFound: results.qualityIssues.length,
        summary: results.summary,
      };
    } catch (error) {
      logger.error("Error analyzing code changes", { error: error.message });
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async analyzeFile(filePath, fileContent) {
    // Use Hugging Face code model to analyze the file
    try {
      const prompt = `
File: ${filePath}

Code:
\`\`\`
${fileContent}
\`\`\`

Analyze this code and identify potential issues. Format your response as JSON with:
1. A brief summary
2. A list of quality issues (each with type, severity, description, suggestion)
3. Overall code quality score (1-10)
`;

      const response = await query(this.codeModel, {
        inputs: prompt,
        parameters: {
          max_new_tokens: 500,
          temperature: 0.3,
        },
      });

      try {
        // Try to parse as JSON
        return JSON.parse(response);
      } catch (e) {
        // Fallback if parsing fails
        return {
          summary: response.slice(0, 200),
          qualityIssues: [],
          score: 5,
        };
      }
    } catch (error) {
      logger.error("Error analyzing file with Hugging Face", {
        file: filePath,
        error: error.message,
      });
      return {
        summary: "Error analyzing file",
        qualityIssues: [],
        score: 0,
      };
    }
  }

  async reviewCode(payload) {
    // Implementation for code review functionality
    // Similar to analyzeChanges but focused on PR review
    return { message: "Code review not yet implemented" };
  }

  async generateTests(payload) {
    // Implementation for test generation
    return { message: "Test generation not yet implemented" };
  }
}

module.exports = CodeAnalyzerAgent;
