"""
Setup script for notification system
"""

import os
import json
from pathlib import Path

def create_env_file():
    """Create .env file with notification configuration"""
    env_content = """# Notification System Configuration
# Fill in your values and rename this file to .env

# Slack Configuration
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CHANNEL=#support-alerts

# Email Configuration
SMTP_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@yourcompany.com

# Monitoring Thresholds
MIN_TICKETS_FOR_ANALYSIS=5
SATISFACTION_THRESHOLD=0.6
VOLUME_THRESHOLD=10
TIME_WINDOW_HOURS=24
COOLDOWN_HOURS=6
"""
    
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists. Backing up to .env.backup")
        env_file.rename('.env.backup')
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with default configuration")
    print("📝 Please edit .env file with your actual values")

def create_slack_webhook_guide():
    """Create guide for setting up Slack webhook"""
    guide = """
# Slack Webhook Setup Guide

## Step 1: Create a Slack App
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Enter app name (e.g., "Support Monitor")
5. Select your workspace

## Step 2: Enable Incoming Webhooks
1. In your app settings, go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to On
3. Click "Add New Webhook to Workspace"
4. Choose the channel where you want notifications
5. Click "Allow"

## Step 3: Copy Webhook URL
1. Copy the webhook URL (starts with https://hooks.slack.com/services/...)
2. Add it to your .env file:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   SLACK_ENABLED=true
   ```

## Step 4: Test
Run the dashboard and use the "Send Slack Test" button in the Category Monitoring section.
"""
    
    with open('SLACK_SETUP.md', 'w') as f:
        f.write(guide)
    
    print("📱 Created SLACK_SETUP.md with detailed instructions")

def create_email_setup_guide():
    """Create guide for setting up email notifications"""
    guide = """
# Email Notification Setup Guide

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Enable 2-Factor Authentication if not already enabled

### Step 2: Generate App Password
1. Go to Google Account > Security
2. Under "2-Step Verification", click "App passwords"
3. Select "Mail" and your device
4. Copy the generated 16-character password

### Step 3: Configure .env file
```
SMTP_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
ADMIN_EMAIL=admin@yourcompany.com
```

## Other Email Providers

### Outlook/Hotmail
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Yahoo
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

### Custom SMTP Server
Contact your IT department for SMTP server details.

## Security Notes
- Never commit your .env file to version control
- Use app passwords instead of your main password
- Consider using environment variables in production
"""
    
    with open('EMAIL_SETUP.md', 'w') as f:
        f.write(guide)
    
    print("📧 Created EMAIL_SETUP.md with detailed instructions")

def create_systemd_service():
    """Create systemd service file for automatic monitoring"""
    service_content = """[Unit]
Description=Support System Category Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/venv/bin/python src/notification_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('support-monitor.service', 'w') as f:
        f.write(service_content)
    
    print("🔧 Created support-monitor.service file")
    print("📝 Edit the paths and run:")
    print("   sudo cp support-monitor.service /etc/systemd/system/")
    print("   sudo systemctl enable support-monitor")
    print("   sudo systemctl start support-monitor")

def main():
    """Main setup function"""
    print("🚀 Setting up Notification System...")
    print()
    
    # Create configuration files
    create_env_file()
    print()
    
    # Create setup guides
    create_slack_webhook_guide()
    print()
    
    create_email_setup_guide()
    print()
    
    # Create systemd service
    create_systemd_service()
    print()
    
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Follow SLACK_SETUP.md for Slack configuration")
    print("3. Follow EMAIL_SETUP.md for email configuration")
    print("4. Test using the dashboard Category Monitoring section")
    print("5. Run 'python src/notification_scheduler.py' for automated monitoring")

if __name__ == "__main__":
    main()