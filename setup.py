from setuptools import setup, find_packages

setup(
    name="cherry",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Core functionality
        "flask>=2.0.0",
        "numpy>=1.19.0",
        "pandas>=1.3.0",
        
        # Database
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=1.4.0",
        "pymongo>=4.0.0",
        
        # AI & ML
        "pinecone>=2.0.0",  # Updated from pinecone-client
        "sentence-transformers>=2.2.0",
        "torch>=1.12.0",
        "transformers>=4.20.0",
        "langchain>=0.0.200",
        "openai>=0.27.0",
        
        # Utilities
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "beautifulsoup4>=4.10.0",
        
        # Testing
        "pytest>=7.0.0",
    ],
)
