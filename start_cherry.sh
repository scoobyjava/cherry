#!/bin/bash
# start_cherry.sh - Robust script to start Cherry AI

set -e  # Exit immediately if a command exits with a non-zero status

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "🚨 Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Set Python command explicitly
PYTHON_CMD=$(which python3)

# Verify Python version (minimum 3.8)
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo "🚨 Python $REQUIRED_VERSION or higher is required. Current version is $PYTHON_VERSION."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🍒 Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
fi

# Activate the virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
else
    echo "🚨 Unable to activate virtual environment."
    exit 1
fi

# Ensure pip is up-to-date
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ No requirements.txt found, skipping dependency installation."
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "🔑 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check critical environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Warning: OPENAI_API_KEY is not set. LLM functionality may be limited."
fi

# Set PYTHONPATH to current directory
export PYTHONPATH=$(pwd)

# Start Cherry AI application
echo "🚀 Starting Cherry AI..."
python main.py
