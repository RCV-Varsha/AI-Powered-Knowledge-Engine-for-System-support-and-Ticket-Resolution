"""
Simple Launcher for AI Support System
"""

import subprocess
import sys
import os
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    
    print("🔍 Checking Environment Configuration...")
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found. Please run: python setup_env.py")
        return False
    
    # Check Gmail app password
    with open('.env', 'r') as f:
        env_content = f.read()
        if 'your_app_password_here' in env_content:
            print("⚠️  Gmail app password not configured!")
            print("📧 Please update SMTP_PASSWORD in .env file with your Gmail app password")
            print("📖 See GMAIL_SETUP.md for detailed instructions")
            return False
    
    print("✅ Environment configuration looks good!")
    return True

def launch_app():
    """Launch the application"""
    
    print("🚀 Launching AI Support System")
    print("=" * 40)
    print()
    print("📋 System Information:")
    print("   • Administrator: Chakra Varshini")
    print("   • Email: chakravarshini395@gmail.com")
    print("   • System: AI-Powered Support Platform")
    print("   • Features: OTP Authentication, Email Notifications, Google Sheets Integration")
    print()
    print("🔑 Admin Access:")
    print("   • Email: chakravarshini395@gmail.com")
    print("   • Authentication: OTP-based (sent to email)")
    print()
    print("🌐 The application will open in your browser...")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        # Launch Streamlit with production app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/production_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")

def main():
    """Main launcher function"""
    
    print("🎫 AI Support System Launcher")
    print("Developed by Chakra Varshini")
    print("=" * 40)
    print()
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Please configure your environment before launching.")
        print("Run: python setup_env.py")
        return
    
    # Launch application
    launch_app()

if __name__ == "__main__":
    main()