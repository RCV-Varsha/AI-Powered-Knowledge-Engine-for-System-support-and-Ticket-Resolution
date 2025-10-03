#!/usr/bin/env python3
"""
Quick launcher for the Streamlit AI Support Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required files exist"""
    required_files = [
        "dashboard.py",
        "article_suggester.py", 
        "src/sheets_client.py",
        "src/resolver.py",
        "src/kb_processor.py",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def install_streamlit_deps():
    """Install Streamlit-specific dependencies"""
    try:
        print("📦 Installing Streamlit dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "plotly"], check=True)
        print("✅ Streamlit dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def run_streamlit_app():
    """Launch the Streamlit app"""
    try:
        print("🚀 Launching Streamlit dashboard...")
        print("📱 The app will open in your browser automatically")
        print("🔗 If it doesn't, visit: http://localhost:8501")
        print("\n⏹️  Press Ctrl+C to stop the application")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.headless", "false",
            "--server.runOnSave", "true"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

def main():
    print("🎫 AI SUPPORT SYSTEM - STREAMLIT LAUNCHER")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Please run this script from the project root directory")
        print("📁 Make sure you're in the AI PROJECT_BATCH1 folder")
        return
    
    # Add src to Python path
    src_path = Path("src").absolute()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Check requirements
    if not check_requirements():
        print("\n🔧 Please ensure all required files are present")
        print("📝 Run setup_environment.py first if you haven't")
        return
    
    # Install dependencies if needed
    try:
        import streamlit
        import plotly
        print("✅ Streamlit dependencies already installed")
    except ImportError:
        if not install_streamlit_deps():
            return
    
    # Run the app
    run_streamlit_app()

if __name__ == "__main__":
    main()