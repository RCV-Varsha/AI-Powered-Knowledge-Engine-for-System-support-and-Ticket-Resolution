#!/usr/bin/env python3
"""
Environment setup script for AI-powered support system
"""

import os
import sys
from pathlib import Path
import json

def create_directory_structure():
    """Create required directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        "data",
        "vectorstore", 
        "logs",
        "results"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    return True

def create_env_file():
    """Create .env file template"""
    print("🔑 Creating .env file template...")
    
    env_template = """# API Keys for LLM providers
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Google Sheets Configuration
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_WORKSHEET_NAME=tickets

# System Configuration
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Vector Store Configuration
VECTORSTORE_PATH=vectorstore/db_faiss
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Categorization Settings
DEFAULT_LLM_PROVIDER=gemini
FALLBACK_TO_TEMPLATE=true
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("   ⚠️ .env file already exists, skipping...")
        return False
    
    with open(env_file, "w") as f:
        f.write(env_template)
    
    print("   ✅ .env file created")
    print("   📝 Please edit .env file with your actual API keys")
    return True

def create_requirements_file():
    """Create requirements.txt file"""
    print("📦 Creating requirements.txt...")
    
    requirements = """# Core dependencies
python-dotenv==1.0.0
langchain-community==0.0.38
langchain-google-genai==1.0.1
langchain-core==0.1.52
langchain-openai==0.0.8

# Vector store and embeddings  
faiss-cpu==1.7.4
sentence-transformers==2.2.2

# Google Sheets integration
gspread==5.12.0
google-auth==2.24.0

# Data processing
pandas==2.1.3
numpy==1.24.3

# Utilities
tqdm==4.66.1
colorama==0.4.6
"""
    
    req_file = Path("requirements.txt")
    if req_file.exists():
        print("   ⚠️ requirements.txt already exists, skipping...")
        return False
    
    with open(req_file, "w") as f:
        f.write(requirements)
    
    print("   ✅ requirements.txt created")
    return True

def create_google_sheets_template():
    """Create Google Sheets template structure"""
    print("📊 Creating Google Sheets template...")
    
    template = {
        "sheet_name": "tickets",
        "headers": [
            "ticket_id",
            "ticket_content", 
            "ticket_cat",
            "ticket_timestamp",
            "ticket_by",
            "ticket_status"
        ],
        "sample_data": [
            {
                "ticket_id": "SAMPLE-001",
                "ticket_content": "Sample ticket for testing system functionality",
                "ticket_cat": "documentation",
                "ticket_timestamp": "2024-01-01T12:00:00",
                "ticket_by": "system",
                "ticket_status": "resolved"
            }
        ]
    }
    
    template_file = Path("data/sheets_template.json")
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2)
    
    print("   ✅ Google Sheets template created at data/sheets_template.json")
    print("   📝 Use this structure when setting up your Google Sheet")
    return True

def create_service_account_template():
    """Create service account template"""
    print("🔐 Creating service account template...")
    
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    template_file = Path("service_account_template.json")
    if template_file.exists():
        print("   ⚠️ service_account_template.json already exists, skipping...")
        return False
    
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2)
    
    print("   ✅ Service account template created")
    print("   📝 Download your actual service account key from Google Cloud Console")
    print("   📝 Replace service_account_template.json with your actual service_account.json")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("   ❌ Python 3.8+ required")
        return False
    else:
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required modules can be imported
    required_modules = [
        "json",
        "os", 
        "pathlib",
        "datetime",
        "uuid"
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (built-in module missing)")
            return False
    
    return True

def display_next_steps():
    """Display next steps for user"""
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60)
    
    steps = [
        "1. 📝 Edit .env file with your API keys",
        "2. 📊 Set up Google Sheet with the template structure",
        "3. 🔑 Download Google service account key and save as service_account.json", 
        "4. 📦 Install dependencies: pip install -r requirements.txt",
        "5. 🧪 Run validation: python validation_script.py",
        "6. 🚀 Start the system: python src/main.py"
    ]
    
    for step in steps:
        print(step)
    
    print("\n📚 Additional Resources:")
    print("   • Google Sheets API: https://developers.google.com/sheets/api")
    print("   • Google AI API Keys: https://makersuite.google.com/app/apikey") 
    print("   • OpenAI API Keys: https://platform.openai.com/api-keys")

def main():
    """Main setup function"""
    print("🚀 AI-POWERED SUPPORT SYSTEM - ENVIRONMENT SETUP")
    print("="*60)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met. Please install required dependencies.")
        return False
    
    print("\n🔧 Setting up environment...")
    
    # Create directory structure
    create_directory_structure()
    
    # Create configuration files
    create_env_file()
    create_requirements_file()
    create_google_sheets_template()
    create_service_account_template()
    
    print("\n✅ Environment setup completed!")
    
    # Display next steps
    display_next_steps()
    
    return True

if __name__ == "__main__":
    main()