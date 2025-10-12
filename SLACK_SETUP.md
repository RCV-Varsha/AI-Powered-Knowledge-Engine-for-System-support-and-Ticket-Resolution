
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
