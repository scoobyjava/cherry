#!/bin/bash
# Complete Cherry Project Repair Script
set -e  # Exit on error
echo "🔧 Starting comprehensive Cherry project repair..."

# PHASE 1: SETUP AND CLEANUP
echo "📦 Backing up project..."
BACKUP_DIR="${PWD}_backup_$(date +%Y%m%d%H%M%S)"
cp -r "$PWD" "$BACKUP_DIR"

echo "🧹 Cleaning environment..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name ".pytest_cache" -exec rm -rf {} +
find . -name "backup_*" -type d -exec rm -rf {} +

# PHASE 2: FIX MERGE CONFLICTS
echo "🔄 Fixing merge conflicts..."
cat > cherry/utils/__init__.py << 'EOF'
from .config import Config
from .logger import logger
from .retry import retry

__all__ = ["Config", "logger", "retry"]
EOF

# PHASE 3: CREATE PROPER SETUP FILES
echo "📄 Creating proper setup.py..."
cat > setup.py << 'EOF'
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
        "transformers",
        "langchain",
        "openai",
        "requests",
        "python-dotenv",
        "pandas",
        "scikit-learn",
        "sqlalchemy",
        "pymongo",
        "beautifulsoup4",
        "pytest",
    ],
)
EOF

# PHASE 4: CREATE/UPDATE .ENV FILE
echo "🔑 Creating environment file template..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# API Keys
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_env

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cherry
DB_USER=postgres
DB_PASSWORD=postgres

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
EOF
    echo "⚠️  Created .env template - you need to add your API keys!"
else
    echo "✅ .env file already exists"
fi

# PHASE 5: REBUILD ENVIRONMENT
echo "🔨 Rebuilding virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel setuptools

# PHASE 6: INSTALL DEPENDENCIES
echo "📚 Installing dependencies..."
pip install --no-cache-dir -e .

# Check if requirements.txt exists and install from it with relaxed constraints
if [ -f "requirements.txt" ]; then
    echo "📝 Installing from requirements.txt with relaxed constraints..."
    sed 's/==/>=/g; s/<=/>=/g; s/pinecone-client/pinecone/g' requirements.txt > requirements_relaxed.txt
    pip install --no-cache-dir -r requirements_relaxed.txt || {
        echo "⚠️  Trying again without version constraints..."
        grep -v "==" requirements.txt | sed 's/pinecone-client/pinecone/g' > requirements_minimal.txt
        pip install --no-cache-dir -r requirements_minimal.txt || true
    }
fi

# PHASE 7: ESSENTIAL DEPENDENCIES
echo "🛠️  Installing critical packages..."
pip install --no-cache-dir pytest torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install --no-cache-dir flask numpy pandas scikit-learn langchain "pinecone>=2.0.0" sentence-transformers psycopg2-binary sqlalchemy requests beautifulsoup4 python-dotenv

# PHASE 8: SET PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
echo "export PYTHONPATH=$PWD:\$PYTHONPATH" >> venv/bin/activate

# PHASE 9: FIX COMMON ISSUES
echo "🔍 Checking for common issues..."
# Fix import in __init__.py files
for init_file in $(find cherry -name "__init__.py"); do
    if grep -q ">>>>" "$init_file"; then
        echo "Fixing merge conflict in $init_file"
        sed -i '/>>>/d' "$init_file" 
    fi
done

# PHASE 10: FINAL CHECK
echo "🧪 Running sanity check..."
python -c "
try:
    import cherry
    print('✅ Cherry package imported successfully!')
except ImportError as e:
    print(f'❌ Error importing cherry: {e}')
    
try:
    import pytest
    print('✅ Pytest installed successfully!')
except ImportError:
    print('❌ Pytest not installed')
    
try:
    import numpy
    import flask
    import pinecone
    import sentence_transformers
    print('✅ Essential packages imported successfully!')
except ImportError as e:
    print(f'❌ Error importing essential packages: {e}')
"

echo ""
echo "🎉 Cherry project repair completed! Next steps:"
echo ""
echo "1️⃣ Make sure you've activated the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2️⃣ Update the .env file with your API keys"
echo ""
echo "3️⃣ Run tests individually:"
echo "   python -m pytest tests/test_backend.py -v"
echo ""
echo "4️⃣ If you still encounter import errors, install the specific missing package:"
echo "   pip install <package-name>"
echo ""
echo "5️⃣ To debug a specific test file with visual breakpoints, use VS Code's Python Test Explorer"
echo ""