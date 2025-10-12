"""
Configuration file for notification system
"""

import os
from pathlib import Path

# Notification System Configuration
NOTIFICATION_CONFIG = {
    # Slack Settings
    "slack": {
        "enabled": False,  # Set to True to enable Slack notifications
        "webhook_url": "",  # Your Slack webhook URL
        "channel": "#support-alerts",  # Channel to send alerts to
    },
    
    # Email Settings
    "email": {
        "enabled": False,  # Set to True to enable email notifications
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "",  # Your email username
        "password": "",  # Your email password or app password
        "admin_email": "",  # Admin email to receive alerts
    },
    
    # Monitoring Thresholds
    "thresholds": {
        "min_tickets_for_analysis": 5,  # Minimum tickets needed to analyze a category
        "satisfaction_threshold": 0.6,  # Alert if satisfaction below 60%
        "volume_threshold": 10,  # Alert if more than 10 tickets in time window
        "time_window_hours": 24,  # Analyze last 24 hours
        "cooldown_hours": 6,  # Don't send duplicate alerts within 6 hours
    },
    
    # File Paths
    "paths": {
        "ticket_log": "ticket_log.jsonl",
        "last_notification": "last_notification.json",
    }
}

def get_config():
    """Get configuration with environment variable overrides"""
    config = NOTIFICATION_CONFIG.copy()
    
    # Override with environment variables if they exist
    if os.getenv('SLACK_ENABLED'):
        config['slack']['enabled'] = os.getenv('SLACK_ENABLED').lower() == 'true'
    if os.getenv('SLACK_WEBHOOK_URL'):
        config['slack']['webhook_url'] = os.getenv('SLACK_WEBHOOK_URL')
    if os.getenv('SLACK_CHANNEL'):
        config['slack']['channel'] = os.getenv('SLACK_CHANNEL')
    
    if os.getenv('SMTP_ENABLED'):
        config['email']['enabled'] = os.getenv('SMTP_ENABLED').lower() == 'true'
    if os.getenv('SMTP_SERVER'):
        config['email']['smtp_server'] = os.getenv('SMTP_SERVER')
    if os.getenv('SMTP_PORT'):
        config['email']['smtp_port'] = int(os.getenv('SMTP_PORT'))
    if os.getenv('SMTP_USERNAME'):
        config['email']['username'] = os.getenv('SMTP_USERNAME')
    if os.getenv('SMTP_PASSWORD'):
        config['email']['password'] = os.getenv('SMTP_PASSWORD')
    if os.getenv('ADMIN_EMAIL'):
        config['email']['admin_email'] = os.getenv('ADMIN_EMAIL')
    
    return config

def create_env_template():
    """Create a .env template file for configuration"""
    env_template = """# Notification System Configuration
# Copy this file to .env and fill in your values

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
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("Created .env.template file. Copy to .env and configure your settings.")