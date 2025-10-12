"""
Production Environment Configuration
"""

import os
from pathlib import Path

# Create .env file with production settings
def create_production_env():
    """Create production environment configuration"""
    
    env_content = f"""# Production Configuration for AI Support System
# Administrator: Chakra Varshini
# Email: chakravarshini395@gmail.com

# Admin Configuration
ADMIN_NAME=Chakra Varshini
ADMIN_EMAIL=chakravarshini395@gmail.com
SYSTEM_NAME=AI Support System
DEVELOPER_NAME=Chakra Varshini

# Email Configuration (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=chakravarshini395@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_SENDER_NAME=Chakra Varshini

# Notification Settings
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=
SLACK_CHANNEL=#support-alerts

# Monitoring Thresholds
SATISFACTION_THRESHOLD=0.6
VOLUME_THRESHOLD=10
TIME_WINDOW_HOURS=24
COOLDOWN_HOURS=6

# Google Sheets Configuration
GOOGLE_SHEETS_ENABLED=true
SERVICE_ACCOUNT_FILE=keys/service-account.json

# Security Settings
OTP_EXPIRY_MINUTES=10
SESSION_TIMEOUT_HOURS=8
MAX_LOGIN_ATTEMPTS=3

# System Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
CACHE_TTL_MINUTES=5
"""
    
    env_file = Path('.env')
    
    if env_file.exists():
        # Remove existing backup if it exists
        backup_file = Path('.env.backup')
        if backup_file.exists():
            backup_file.unlink()
        
        # Create backup
        env_file.rename(backup_file)
        print(f"📁 Backed up existing .env to {backup_file}")
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Created production .env configuration file")
    print("📝 Please update SMTP_PASSWORD with your Gmail app password")

def setup_gmail_app_password():
    """Instructions for setting up Gmail app password"""
    
    instructions = """
# Gmail App Password Setup Instructions

## Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Enable 2-Step Verification if not already enabled

## Step 2: Generate App Password
1. In Google Account settings, go to Security
2. Under "2-Step Verification", click "App passwords"
3. Select "Mail" as the app
4. Select "Other" as the device and enter "AI Support System"
5. Click "Generate"
6. Copy the 16-character password (e.g., abcd efgh ijkl mnop)

## Step 3: Update Configuration
1. Open the .env file
2. Replace "your_app_password_here" with your 16-character app password
3. Save the file

## Step 4: Test Email
1. Run the application
2. Go to Admin Dashboard → Notifications
3. Click "Send Test Email" to verify email functionality

## Security Notes
- Never share your app password
- The app password is different from your regular Gmail password
- You can revoke app passwords anytime from Google Account settings
"""
    
    with open('GMAIL_SETUP.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("📧 Created GMAIL_SETUP.md with detailed instructions")

def create_production_launcher():
    """Create production launcher script"""
    
    launcher_content = '''"""
Production Launcher for AI Support System
Developed by Chakra Varshini
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
        print("❌ .env file not found. Creating default configuration...")
        from production_config import create_production_env
        create_production_env()
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

def launch_production_app():
    """Launch the production application"""
    
    print("🚀 Launching AI Support System (Production)")
    print("=" * 50)
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
        print("\\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")

def main():
    """Main launcher function"""
    
    print("🎫 AI Support System - Production Launcher")
    print("Developed by Chakra Varshini")
    print("=" * 50)
    print()
    
    # Check environment
    if not check_environment():
        print("\\n⚠️  Please configure your environment before launching.")
        return
    
    # Launch application
    launch_production_app()

if __name__ == "__main__":
    main()
'''
    
    with open('launch_production.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ Created production launcher script")

def main():
    """Setup production environment"""
    
    print("🔧 Setting up Production Environment")
    print("=" * 40)
    print()
    
    # Create configuration files
    create_production_env()
    print()
    
    setup_gmail_app_password()
    print()
    
    create_production_launcher()
    print()
    
    print("✅ Production environment setup completed!")
    print()
    print("Next steps:")
    print("1. Update SMTP_PASSWORD in .env file with your Gmail app password")
    print("2. Follow GMAIL_SETUP.md for detailed email configuration")
    print("3. Run: python launch_production.py")
    print("4. Access admin with email: chakravarshini395@gmail.com")

if __name__ == "__main__":
    main()
