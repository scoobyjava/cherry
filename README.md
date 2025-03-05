# Cherry 🍒

Cherry is an advanced orchestration framework for AI agents, designed to handle complex workflows with robust error handling, recovery mechanisms, and efficient task coordination.

## Features

- Agent management and orchestration
- Robust error handling and recovery strategies
- Task dependency management
- Memory system integration
- Workflow execution with fallback mechanisms

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

## Project Structure

- `cherry/core/`: Core orchestration functionality
- `cherry/memory/`: Memory management components
- `cherry/agents/`: Agent implementations

## License

[MIT License](LICENSE)

# 🍒 Cherry AI: Autonomous Multi-Agent Innovation System

## 🌟 Project Overview

Cherry AI is an advanced, flexible multi-agent AI system designed to tackle complex problem-solving tasks through intelligent agent collaboration, creative ideation, and adaptive learning.

### 🚀 Key Features

- Dynamic Multi-Agent Orchestration
- Creative Problem-Solving Capabilities
- Skill-Based Agent Architecture
- Advanced Memory Management
- Scalable Task Handling

## 🔧 Installation

### Prerequisites

- Python 3.9+
- OpenAI API Key

### Setup Steps

1. Clone the repository:

```bash
git clone https://github.com/yourusername/cherry-ai.git
cd cherry-ai
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Setup

1. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory and add the following environment-specific settings:
   ```plaintext
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///your_database.db
   ```

## Secret Management

This project uses a secure approach to manage API keys and other sensitive information:

### Setup Instructions

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Add your actual API keys to the `.env` file:

   ```
   OPENAI_API_KEY=sk-your-actual-key
   PINECONE_API_KEY=your-actual-pinecone-key
   # Other keys as needed
   ```

3. For Docker/Kubernetes environments, you can use file-based secrets:
   - Create a directory for secrets: `/run/secrets/`
   - Add individual files named after each secret key

### Supported Secret Providers

- **Environment Variables**: Default method, uses process.env
- **File**: Reads secrets from files in a designated directory
- **AWS Secrets Manager**: (Requires additional implementation)
- **Google Secret Manager**: (Requires additional implementation)
- **HashiCorp Vault**: (Requires additional implementation)

### Using Secrets in Configuration

In configuration files, reference secrets using the syntax:

```
${SECRET:KEY_NAME:provider_type}
```

Example:

```json
{
  "api_key": "${SECRET:OPENAI_API_KEY:env_var}"
}
```

If provider_type is omitted, it will use the default provider (environment variables).

## 🎬 Quick Start

### Basic Usage

```python
from cherry.agents.creative_agent import CreativeAgent

# Initialize the Creative Agent
agent = CreativeAgent(name="InnovationExplorer")

# Solve a complex problem
result = agent.solve_complex_problem(
    "Develop sustainable urban transportation solutions",
    constraints={
        "budget": "Limited",
        "environmental_impact": "Minimize carbon emissions"
    }
)

# Print the innovative solutions
print(result)
```

## 📂 Project Structure

```
cherry_ai/
│
├── cherry/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── creative_agent.py
│   │   └── research_agent.py
│   │
│   ├── core/
│   │   ├── orchestrator.py
│   │   └── memory.py
│   │
│   └── utils/
│       └── config.py
│
├── tests/
├── examples/
├── docs/
├── requirements.txt
└── README.md
```

## 🤝 Contributing

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .  # Install in editable mode

# Run tests
pytest tests/

# Code formatting
black .
flake8 .
```

## 🧠 Roadmap

- [ ] Expand Agent Skill Sets
- [ ] Implement Advanced Memory Consolidation
- [ ] Add More Specialized Agents
- [ ] Develop Comprehensive Documentation
- [ ] Create Advanced Task Orchestration Mechanisms

## Dependency Management

This project uses the following dependencies:

- Flask==2.1.3
- requests==2.28.1
- numpy==1.23.5
- pandas==1.5.3
- scikit-learn==1.1.3

It is important to keep these dependencies up-to-date to avoid security vulnerabilities and ensure compatibility. You can update the dependencies by running:

```
pip install --upgrade -r requirements.txt
```

## Configuration Refactoring

### Identified Redundant Code Patterns

After analyzing the `benchmark_config.json` file, the following redundant patterns were identified:

1. **Connection Configurations**: Similar timeout and retry logic across different services
2. **Backup Configurations**: Common backup settings (schedule, retention, validation) with slight variations
3. **Namespace Definitions**: Similar structure with repeated fields and only some variations
4. **Validation Patterns**: Common validation approaches across different components

### Refactoring Strategy

The refactoring approach takes advantage of:

1. **Template-based Configuration**: Common patterns extracted into reusable templates
2. **Inheritance and Composition**: Base configurations extended with specific overrides
3. **Dynamic Configuration Generation**: Using JavaScript to programmatically create configurations
4. **Schema Validation**: Ensuring all configurations follow the required structure

### Usage

To generate a configuration:

```javascript
const { generateBenchmarkConfig } = require("./config/config_generator");

const config = generateBenchmarkConfig(process.env);
console.log(JSON.stringify(config, null, 2));
```

### Benefits

- **Reduced Duplication**: Common patterns defined once, reused everywhere
- **Improved Maintainability**: Changes to common patterns only need to be made in one place
- **Consistent Configuration**: Ensures all services follow the same patterns
- **Type Safety**: Schema validation helps catch errors early

## Code Complexity Analysis

The project includes tools to analyze code complexity and identify potential problem areas that might need refactoring.

### Usage

```bash
# Basic usage - analyze a directory
npm run analyze-complexity src/

# Analyze with custom thresholds
npm run analyze-complexity --threshold-cc 15 --threshold-mi 60 src/

# Generate a JSON report
npm run analyze-complexity --format json --output complexity-report.json src/

# Use a custom configuration file
npm run analyze-complexity --config ./my-config.json src/
```

### Configuration

The code complexity analyzer can be configured through a JSON file. The default configuration is in `config/complexity-analysis.json`.

Example configuration:

```json
{
  "thresholds": {
    "cyclomaticComplexity": 10,
    "maintainabilityIndex": 65
  },
  "ignorePatterns": ["/node_modules/", "\\.test\\."],
  "reportFormat": "detailed"
}
```

### Metrics Explained

- **Cyclomatic Complexity (CC)**: Measures the number of linearly independent paths through the code. Higher values (>10) indicate code that may be difficult to test and maintain.
- **Maintainability Index (MI)**: A composite metric that considers cyclomatic complexity, lines of code, and Halstead volume. Values below 65 suggest code that might be difficult to maintain.
- **Halstead Difficulty**: Represents how difficult the code is to understand. Higher values indicate more complex code.

- **Parameter Count**: The number of parameters in functions. Functions with many parameters (>4) may be doing too much.

### Interpreting Results

The analyzer highlights files and functions that exceed recommended thresholds. Consider refactoring:

- Functions with high cyclomatic complexity (>10)
- Files with low maintainability index (<65)
- Functions with too many parameters (>4)
- Files with multiple complex functions

## Code Quality Tools

### Function Complexity Analyzer

The project includes a code analyzer tool that helps identify overly complex functions and methods based on their length. This tool can be used to maintain code quality and identify refactoring opportunities.

#### Usage

```bash
# Basic usage - scans current directory with default settings
python tools/code_analyzer.py

# Scan a specific directory
python tools/code_analyzer.py --directory ./src

# Use custom thresholds
python tools/code_analyzer.py --warning 30 --error 60

# Use configuration file
python tools/code_analyzer.py --config tools/analyzer_config.json

# Save report to file
python tools/code_analyzer.py --output complexity_report.json
```

#### Configuration

You can configure the analyzer using command-line arguments or a JSON configuration file. The default configuration defines:

- Warning threshold: 40 lines
- Error threshold: 80 lines
- Supported file extensions: .py, .js, .ts, .jsx, .tsx
- Excluded directories: node_modules, venv, .git, **pycache**, dist, build

Example configuration file (analyzer_config.json):

```json
{
  "warning_threshold": 40,
  "error_threshold": 80,
  "file_extensions": [".py", ".js", ".ts", ".jsx", ".tsx"],
  "exclude_dirs": [
    "node_modules",
    "venv",
    ".git",
    "__pycache__",
    "dist",
    "build"
  ],
  "exclude_files": ["generated_*.py", "*.min.js"]
}
```

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🚨 Disclaimer

Cherry AI is an experimental project. Use with caution and always verify critical outputs.

## 📞 Contact

- Project Lead: Lynn Patrick Musil
- Email: Lynn@payready.com
- Project Link: [https://github.com/yourusername/cherry-ai]

## 🌈 Inspiration

Inspired by the potential of multi-agent AI systems to solve complex, interdisciplinary challenges.

# Cherry - AI Orchestration Framework

## Environment Configuration

Cherry requires several environment variables to be set for connecting to external services like Pinecone, Chroma, and various LLM providers.

### Setting Up Environment Variables

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys and configuration:

   ```
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=your_pinecone_environment_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Never commit your `.env` file to version control. It's already included in .gitignore.

### Required Environment Variables

- `PINECONE_API_KEY`: Your Pinecone API key for vector storage
- `PINECONE_ENVIRONMENT`: Your Pinecone environment name
- `OPENAI_API_KEY`: Your OpenAI API key for LLM access

### Optional Environment Variables

- `CHROMA_HOST`: Host for Chroma DB (defaults to local instance)
- `CHROMA_PORT`: Port for Chroma DB
- `ANTHROPIC_API_KEY`: Your Anthropic API key if using Claude models
- `CHERRY_LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR, CRITICAL)

## Installation and Setup

[Installation instructions here]

# Cherry Project

## Overview

Cherry is a project that...

## Installation

```bash
git clone https://github.com/username/cherry.git
cd cherry
npm install
```

## SSH Access

To grant external AI access to this repository, follow these steps:

1. Ensure you have an SSH key pair. If not, generate one using:

   ```sh
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   ```

2. Add the public key to the repository's deploy keys. You can find the public key in `ssh/deploy_key.pub`.

3. Configure the external AI system to use the corresponding private key for authentication.

4. Use the SSH clone URL (e.g., `git@github.com:username/repository.git`) when interacting with the repository.

# Cherry: AI Deployment and Testing Framework

Cherry provides a comprehensive framework for testing, evaluating, and deploying AI systems in controlled environments with robust feedback mechanisms.

## System Architecture

Cherry consists of several integrated components:

1. **Simulation Framework**: Creates fully sandboxed environments to test behavior without external dependencies.
2. **Staging Deployment**: Tests interactions with (mock) real-world APIs and databases in a controlled setting.
3. **Learning System**: Analyzes reports from simulations and staging to identify trends and suggest improvements.
4. **Integration Layer**: Coordinates the workflow across all components.

## Getting Started

### Prerequisites

- Python 3.8+
- Dependencies in `requirements.txt`

### Installation

```bash
# Clone the repository
git clone https://github.com/ai-cherry/cherry.git
cd cherry

# Install dependencies
pip install -r requirements.txt
```
