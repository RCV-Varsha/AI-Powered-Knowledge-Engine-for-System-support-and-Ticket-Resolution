
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
