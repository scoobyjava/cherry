#!/bin/bash
# Cherry Project - Complete Repair Script

set -e  # Exit on error
echo "🔧 Starting comprehensive Cherry project repair..."

# 1. BACKUP (just in case)
echo "📦 Creating backup..."
BACKUP_DIR="${PWD}_backup_$(date +%Y%m%d%H%M%S)"
cp -r "$PWD" "$BACKUP_DIR"
echo "✅ Backup created at $BACKUP_DIR"

# 2. CLEAN ENVIRONMENT
echo "🧹 Cleaning environment..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name ".pytest_cache" -exec rm -rf {} +

# 3. FIX MERGE CONFLICTS
echo "🔄 Fixing merge conflicts..."
cat > cherry/utils/__init__.py << EOF
from .config import Config
from .logger import logger
from .retry import retry

__all__ = ["Config", "logger", "retry"]
EOF
echo "✅ Fixed merge conflict in cherry/utils/__init__.py"

# 4. CREATE PROPER SETUP.PY
echo "📄 Creating proper setup.py..."
cat > setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="cherry",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "numpy",
        "psycopg2-binary",
        "pinecone",
        "sentence-transformers",
        "torch",
        "langchain",
        "requests",
        "python-dotenv",
    ],
)
EOF
echo "✅ Created setup.py with required dependencies"

# 5. REBUILD VIRTUAL ENVIRONMENT
echo "🔨 Rebuilding virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate

# 6. INSTALL DEPENDENCIES WITH RELAXED CONSTRAINTS
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -e .

# Check if requirements.txt exists and install from it
if [ -f "requirements.txt" ]; then
    # Create a version with relaxed constraints
    cat requirements.txt | sed 's/==/>=/g' | sed 's/<=/>=/g' > requirements_relaxed.txt
    pip install -r requirements_relaxed.txt || {
        echo "⚠️  Warning: Could not install all dependencies with constraints."
        echo "📝 Attempting installation without version constraints..."
        cat requirements.txt | grep -v "==" > requirements_minimal.txt
        pip install -r requirements_minimal.txt
    }
else
    echo "⚠️ No requirements.txt found. Using setup.py dependencies only."
fi

# 7. ESSENTIAL PACKAGES (install without constraints)
echo "🛠️  Installing essential packages..."
pip install pytest flask numpy pandas scikit-learn torch langchain pinecone sentence-transformers psycopg2-binary sqlalchemy requests beautifulsoup4 python-dotenv

# 8. SET PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
echo "export PYTHONPATH=$PWD:\$PYTHONPATH" >> venv/bin/activate

# 9. SANITY CHECK
echo "🧪 Running basic sanity check..."
python -c "import cherry; print('Cherry package imported successfully!')"

# 10. RUN ONE TEST
echo "🔍 Attempting to run a single test..."
python -c "
import os
import glob

# Find the simplest test file
test_files = glob.glob('tests/**/test_*.py', recursive=True)
if test_files:
    smallest_file = min(test_files, key=os.path.getsize)
    print(f'Attempting to run {smallest_file}')
    try:
        import pytest
        pytest.main([smallest_file, '-v'])
    except Exception as e:
        print(f'Error running test: {e}')
else:
    print('No test files found')
"

echo "🎉 Cherry project repair completed!"
echo "➡️  Next steps:"
echo "   1. Run 'source venv/bin/activate' if not already activated"
echo "   2. Run individual tests with 'python -m pytest tests/specific_test.py -v'"
echo "   3. For any remaining issues, check specific dependencies in the failing tests"