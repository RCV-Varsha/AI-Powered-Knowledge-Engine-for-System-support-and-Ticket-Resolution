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
1. Run: python launch_production.py
2. Go to Admin Dashboard → Notifications
3. Click "Send Test Email" to verify email functionality

## Security Notes
- Never share your app password
- The app password is different from your regular Gmail password
- You can revoke app passwords anytime from Google Account settings
