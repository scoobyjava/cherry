# Code Complexity Analysis

This tool helps identify overly complex function and method implementations across the codebase. Complex functions are often harder to maintain, test, and understand, making them prime candidates for refactoring.

## Usage

Run the code analyzer with:

```bash
# Basic usage (analyzes current directory)
python tools/code_analyzer.py

# Analyze specific directory
python tools/code_analyzer.py --root /workspaces/cherry/src

# Save results to a file
python tools/code_analyzer.py --output complexity-report.json

# Exclude specific directories
python tools/code_analyzer.py --exclude node_modules venv dist build

# Use custom complexity thresholds
python tools/code_analyzer.py --thresholds tools/complexity_thresholds.json
```

## Configuration

The tool uses line count as the primary metric for complexity. Default thresholds are:
- Python: 50 lines
- JavaScript/TypeScript: 40 lines
- Java/Go/C#/C++: 50 lines

You can customize these thresholds by creating a JSON file and using the `--thresholds` option.

## Understanding the Report

The generated report contains:
1. A summary of all complex functions found
2. Breakdown by programming language
3. Detailed information for each function:
   - Name
   - Line count
   - File path
   - Start and end line numbers
   - Language

## Best Practices for Refactoring

When refactoring complex functions, consider:

1. **Extraction**: Break large functions into smaller, focused functions
2. **Single Responsibility**: Ensure each function does one thing well
3. **Reduce Nesting**: Excessive nesting increases cognitive load
4. **Early Returns**: Use early returns to avoid deep nesting
5. **Parameterization**: Replace duplicated code with parameters
6. **Remove Dead Code**: Delete unused or redundant code

## Integration

Consider integrating this tool into your CI/CD pipeline to:
1. Monitor code complexity trends over time
2. Prevent merging of overly complex functions
3. Set complexity budgets for different parts of the codebase

## Limitations

This tool primarily focuses on line count as a complexity metric. For a more comprehensive analysis, consider complementing with:
- Cyclomatic complexity measurement
- Cognitive complexity measurement
- Code duplication detection
