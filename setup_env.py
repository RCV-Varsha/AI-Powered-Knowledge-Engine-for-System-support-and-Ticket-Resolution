"""
Simple Environment Setup Script
Fixes the backup issue and creates a single .env file
"""

import os
from pathlib import Path

def setup_environment():
    """Setup environment configuration"""
    
    print("🔧 Setting up Environment Configuration")
    print("=" * 40)
    
    # Remove any existing backup files
    backup_files = ['.env.backup', '.env.old', '.env.temp']
    for backup_file in backup_files:
        if Path(backup_file).exists():
            Path(backup_file).unlink()
            print(f"🗑️  Removed old backup: {backup_file}")
    
    # Create .env file
    env_content = """# AI Support System Configuration
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
    
    # Write .env file
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Created .env configuration file")
    print("📝 Please update SMTP_PASSWORD with your Gmail app password")
    
    # Create Gmail setup instructions
    gmail_instructions = """# Gmail App Password Setup Instructions

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
1. Run: python launch_production.py
2. Go to Admin Dashboard → Notifications
3. Click "Send Test Email" to verify email functionality

## Security Notes
- Never share your app password
- The app password is different from your regular Gmail password
- You can revoke app passwords anytime from Google Account settings
"""
    
    with open('GMAIL_SETUP.md', 'w', encoding='utf-8') as f:
        f.write(gmail_instructions)
    
    print("📧 Created GMAIL_SETUP.md with detailed instructions")
    
    # Create .gitignore if it doesn't exist
    if not Path('.gitignore').exists():
        gitignore_content = """# Environment variables (contains sensitive information)
.env
.env.local
.env.production
.env.backup

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
myenv/
venv/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
log/

# Data files
*.json
*.jsonl
*.csv
*.xlsx
*.xls

# Session files
sessions.json
otp_sessions.json
admin_sessions.json
manual_reviews.json
admins.json
users.json

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Streamlit
.streamlit/

# Jupyter Notebook
.ipynb_checkpoints

# pytest
.pytest_cache/

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
        
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print("📁 Created .gitignore file")
    
    print()
    print("✅ Environment setup completed!")
    print()
    print("Next steps:")
    print("1. Update SMTP_PASSWORD in .env file with your Gmail app password")
    print("2. Follow GMAIL_SETUP.md for detailed email configuration")
    print("3. Run: python launch_production.py")

if __name__ == "__main__":
    setup_environment()
