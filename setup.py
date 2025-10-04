#!/usr/bin/env python3
"""
Setup script for the Financial Multi-Agent Chatbot

This script helps set up the environment and dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def create_directories():
    """Create necessary directories."""
    directories = [
        "storage",
        "storage/chroma_db",
        "storage/uploads",
        "storage/temp",
        "logs",
        "test_documents"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def setup_environment():
    """Set up environment configuration."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your OpenAI API key")
        else:
            print("❌ env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True


def verify_openai_key():
    """Verify OpenAI API key is set."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            print("⚠️  OpenAI API key not set in .env file")
            print("Please edit .env file and add your OpenAI API key")
            return False
        
        print("✅ OpenAI API key is configured")
        return True
    except ImportError:
        print("⚠️  python-dotenv not installed, cannot verify API key")
        return False


def test_imports():
    """Test if all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        import openai
        import chromadb
        import PyPDF2
        import scipy
        import sklearn
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def create_sample_data():
    """Create sample data for testing."""
    sample_csv = """date,revenue,costs,profit
2023-01-01,100000,60000,40000
2023-02-01,110000,65000,45000
2023-03-01,120000,70000,50000
2023-04-01,115000,68000,47000
2023-05-01,130000,75000,55000
2023-06-01,125000,72000,53000
2023-07-01,140000,80000,60000
2023-08-01,135000,78000,57000
2023-09-01,150000,85000,65000
2023-10-01,145000,82000,63000
2023-11-01,160000,90000,70000
2023-12-01,155000,88000,67000"""
    
    sample_pdf_text = """Financial Report Q4 2023

Executive Summary:
Our company achieved record revenue of $1.8M in Q4 2023, representing a 15% increase from Q3. 
The growth was driven by strong performance in our core business segments and successful 
expansion into new markets.

Key Financial Metrics:
- Revenue: $1,800,000 (↑15% QoQ)
- Net Profit: $450,000 (↑12% QoQ)
- Operating Margin: 25%
- Customer Acquisition Cost: $150 (↓8% QoQ)

Strategic Initiatives:
1. Market Expansion: Successfully entered 3 new geographic markets
2. Product Innovation: Launched 2 new product lines
3. Operational Efficiency: Reduced costs by 8% through automation

Risk Factors:
- Increased competition in core markets
- Supply chain disruptions affecting 5% of operations
- Regulatory changes requiring compliance updates

Outlook:
We expect continued growth in Q1 2024 with projected revenue of $1.9M. 
Key focus areas include customer retention and operational scaling."""
    
    # Create sample files
    with open("test_documents/sample_financial_data.csv", "w") as f:
        f.write(sample_csv)
    
    with open("test_documents/sample_financial_report.txt", "w") as f:
        f.write(sample_pdf_text)
    
    print("✅ Created sample test data")


def main():
    """Main setup function."""
    print("🚀 Setting up Financial Multi-Agent Chatbot")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed during environment setup")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed during import testing")
        sys.exit(1)
    
    # Verify OpenAI key
    verify_openai_key()
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run the application: python main.py")
    print("3. Test the API: python test_api.py")
    print("4. Access the API docs at: http://localhost:8000/docs")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()

