"""
Notification System for Category Performance Monitoring
Monitors ticket categories and sends alerts when performance drops below thresholds
"""

import json
import logging
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NotificationConfig:
    """Configuration for notification system"""
    # Slack settings
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    slack_channel: str = "#support-alerts"
    
    # SMTP settings
    smtp_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    admin_email: str = ""
    
    # Monitoring thresholds
    min_tickets_for_analysis: int = 5
    satisfaction_threshold: float = 0.6  # 60% satisfaction rate
    volume_threshold: int = 10  # Alert if more than 10 tickets in category
    time_window_hours: int = 24  # Analyze last 24 hours
    
    # Notification frequency control
    cooldown_hours: int = 6  # Don't send duplicate alerts within 6 hours
    last_notification_file: str = "last_notification.json"

class CategoryPerformanceMonitor:
    """Monitors category performance and triggers notifications"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.ticket_log_path = Path("ticket_log.jsonl")
        self.last_notification_path = Path(config.last_notification_file)
        
    def analyze_category_performance(self) -> Dict[str, Dict]:
        """
        Analyze category performance from ticket logs
        
        Returns:
            Dict with category performance metrics
        """
        if not self.ticket_log_path.exists():
            logger.warning("Ticket log file not found")
            return {}
        
        # Calculate time window
        cutoff_time = datetime.now() - timedelta(hours=self.config.time_window_hours)
        
        category_stats = {}
        
        try:
            with open(self.ticket_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Parse timestamp
                        timestamp_str = entry.get('timestamp', '')
                        if timestamp_str:
                            entry_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if entry_time < cutoff_time:
                                continue
                        
                        category = entry.get('category', 'unknown')
                        user_satisfied = entry.get('user_satisfied', False)
                        
                        if category not in category_stats:
                            category_stats[category] = {
                                'total_tickets': 0,
                                'satisfied_tickets': 0,
                                'unsatisfied_tickets': 0,
                                'satisfaction_rate': 0.0,
                                'recent_tickets': []
                            }
                        
                        category_stats[category]['total_tickets'] += 1
                        if user_satisfied:
                            category_stats[category]['satisfied_tickets'] += 1
                        else:
                            category_stats[category]['unsatisfied_tickets'] += 1
                        
                        # Store recent ticket info
                        category_stats[category]['recent_tickets'].append({
                            'ticket_id': entry.get('ticket_id', ''),
                            'content': entry.get('ticket_content', '')[:100],
                            'satisfied': user_satisfied,
                            'timestamp': timestamp_str
                        })
                        
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing log entry: {e}")
                        continue
            
            # Calculate satisfaction rates
            for category, stats in category_stats.items():
                if stats['total_tickets'] > 0:
                    stats['satisfaction_rate'] = stats['satisfied_tickets'] / stats['total_tickets']
            
            return category_stats
            
        except Exception as e:
            logger.error(f"Error analyzing category performance: {e}")
            return {}
    
    def identify_problematic_categories(self, category_stats: Dict[str, Dict]) -> List[Dict]:
        """
        Identify categories that need admin attention
        
        Returns:
            List of problematic category reports
        """
        problematic_categories = []
        
        for category, stats in category_stats.items():
            # Skip if not enough tickets for analysis
            if stats['total_tickets'] < self.config.min_tickets_for_analysis:
                continue
            
            issues = []
            
            # Check satisfaction rate
            if stats['satisfaction_rate'] < self.config.satisfaction_threshold:
                issues.append({
                    'type': 'low_satisfaction',
                    'message': f"Satisfaction rate {stats['satisfaction_rate']:.1%} below threshold {self.config.satisfaction_threshold:.1%}",
                    'severity': 'high' if stats['satisfaction_rate'] < 0.3 else 'medium'
                })
            
            # Check volume
            if stats['total_tickets'] > self.config.volume_threshold:
                issues.append({
                    'type': 'high_volume',
                    'message': f"High volume: {stats['total_tickets']} tickets in {self.config.time_window_hours}h",
                    'severity': 'medium'
                })
            
            # Check for consecutive unsatisfied tickets
            recent_unsatisfied = sum(1 for ticket in stats['recent_tickets'][-5:] if not ticket['satisfied'])
            if recent_unsatisfied >= 3:
                issues.append({
                    'type': 'consecutive_failures',
                    'message': f"{recent_unsatisfied} of last 5 tickets unsatisfied",
                    'severity': 'high'
                })
            
            if issues:
                problematic_categories.append({
                    'category': category,
                    'stats': stats,
                    'issues': issues,
                    'priority': 'high' if any(issue['severity'] == 'high' for issue in issues) else 'medium'
                })
        
        return problematic_categories
    
    def should_send_notification(self, category: str) -> bool:
        """Check if we should send notification based on cooldown period"""
        if not self.last_notification_path.exists():
            return True
        
        try:
            with open(self.last_notification_path, 'r') as f:
                last_notifications = json.load(f)
            
            last_time_str = last_notifications.get(category)
            if not last_time_str:
                return True
            
            last_time = datetime.fromisoformat(last_time_str)
            cooldown_period = timedelta(hours=self.config.cooldown_hours)
            
            return datetime.now() - last_time > cooldown_period
            
        except Exception as e:
            logger.error(f"Error checking notification cooldown: {e}")
            return True
    
    def update_notification_timestamp(self, category: str):
        """Update the last notification timestamp for a category"""
        try:
            last_notifications = {}
            if self.last_notification_path.exists():
                with open(self.last_notification_path, 'r') as f:
                    last_notifications = json.load(f)
            
            last_notifications[category] = datetime.now().isoformat()
            
            with open(self.last_notification_path, 'w') as f:
                json.dump(last_notifications, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating notification timestamp: {e}")

class SlackNotifier:
    """Handles Slack notifications"""
    
    def __init__(self, webhook_url: str, channel: str = "#support-alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send_alert(self, problematic_categories: List[Dict]) -> bool:
        """Send Slack alert for problematic categories"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            # Create Slack message
            message = self._create_slack_message(problematic_categories)
            
            payload = {
                "channel": self.channel,
                "username": "Support Monitor",
                "icon_emoji": ":warning:",
                "text": message
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Slack notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _create_slack_message(self, problematic_categories: List[Dict]) -> str:
        """Create formatted Slack message"""
        if not problematic_categories:
            return "✅ All categories performing well!"
        
        message = f"🚨 *Support Category Alert* - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        for category_report in problematic_categories:
            category = category_report['category']
            stats = category_report['stats']
            issues = category_report['issues']
            priority = category_report['priority']
            
            priority_emoji = "🔴" if priority == 'high' else "🟡"
            message += f"{priority_emoji} *{category.upper()}*\n"
            message += f"   📊 Satisfaction: {stats['satisfaction_rate']:.1%} ({stats['satisfied_tickets']}/{stats['total_tickets']})\n"
            message += f"   📈 Volume: {stats['total_tickets']} tickets in {self.config.time_window_hours}h\n"
            
            for issue in issues:
                severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡"
                message += f"   {severity_emoji} {issue['message']}\n"
            
            message += "\n"
        
        message += "💡 *Recommended Actions:*\n"
        message += "• Review knowledge base articles for these categories\n"
        message += "• Check if solutions need improvement\n"
        message += "• Consider additional training or documentation\n"
        
        return message

class EmailNotifier:
    """Handles email notifications"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send_alert(self, problematic_categories: List[Dict]) -> bool:
        """Send email alert for problematic categories"""
        if not self.config.smtp_enabled or not self.config.admin_email:
            logger.warning("Email notifications not configured")
            return False
        
        try:
            # Create email content
            subject, body = self._create_email_content(problematic_categories)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = self.config.admin_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.config.smtp_username, self.config.admin_email, text)
            server.quit()
            
            logger.info("Email notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _create_email_content(self, problematic_categories: List[Dict]) -> Tuple[str, str]:
        """Create email subject and HTML body"""
        if not problematic_categories:
            subject = "✅ Support System Status - All Categories Performing Well"
            body = """
            <html>
            <body>
                <h2>Support System Status Report</h2>
                <p>All categories are performing within acceptable thresholds.</p>
                <p><strong>Report Time:</strong> {}</p>
            </body>
            </html>
            """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return subject, body
        
        high_priority_count = sum(1 for cat in problematic_categories if cat['priority'] == 'high')
        subject = f"🚨 Support Alert - {high_priority_count} High Priority Category Issues"
        
        body = f"""
        <html>
        <body>
            <h2>Support Category Performance Alert</h2>
            <p><strong>Report Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Analysis Period:</strong> Last {self.config.time_window_hours} hours</p>
            
            <h3>Problematic Categories:</h3>
        """
        
        for category_report in problematic_categories:
            category = category_report['category']
            stats = category_report['stats']
            issues = category_report['issues']
            priority = category_report['priority']
            
            priority_color = "#ff4444" if priority == 'high' else "#ffaa00"
            body += f"""
            <div style="border-left: 4px solid {priority_color}; padding-left: 10px; margin: 10px 0;">
                <h4 style="color: {priority_color};">{category.upper()} ({priority.upper()} PRIORITY)</h4>
                <p><strong>Satisfaction Rate:</strong> {stats['satisfaction_rate']:.1%} ({stats['satisfied_tickets']}/{stats['total_tickets']} tickets)</p>
                <p><strong>Volume:</strong> {stats['total_tickets']} tickets in {self.config.time_window_hours} hours</p>
                <ul>
            """
            
            for issue in issues:
                severity_color = "#ff4444" if issue['severity'] == 'high' else "#ffaa00"
                body += f"<li style='color: {severity_color};'>{issue['message']}</li>"
            
            body += """
                </ul>
            </div>
            """
        
        body += """
            <h3>Recommended Actions:</h3>
            <ul>
                <li>Review knowledge base articles for these categories</li>
                <li>Check if solutions need improvement or updating</li>
                <li>Consider additional training or documentation</li>
                <li>Analyze common patterns in unsatisfied tickets</li>
            </ul>
            
            <p><em>This is an automated alert from the Support System Monitor.</em></p>
        </body>
        </html>
        """
        
        return subject, body

class NotificationManager:
    """Main notification manager that coordinates all notification types"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.monitor = CategoryPerformanceMonitor(config)
        
        # Initialize notifiers
        self.slack_notifier = None
        if config.slack_enabled and config.slack_webhook_url:
            self.slack_notifier = SlackNotifier(config.slack_webhook_url, config.slack_channel)
        
        self.email_notifier = None
        if config.smtp_enabled:
            self.email_notifier = EmailNotifier(config)
    
    def check_and_notify(self) -> Dict[str, bool]:
        """
        Main method to check category performance and send notifications
        
        Returns:
            Dict with notification results
        """
        logger.info("Starting category performance check...")
        
        # Analyze performance
        category_stats = self.monitor.analyze_category_performance()
        if not category_stats:
            logger.info("No category data found for analysis")
            return {"status": "no_data"}
        
        # Identify problematic categories
        problematic_categories = self.monitor.identify_problematic_categories(category_stats)
        
        if not problematic_categories:
            logger.info("All categories performing well - no notifications needed")
            return {"status": "all_good"}
        
        logger.info(f"Found {len(problematic_categories)} problematic categories")
        
        # Send notifications
        results = {"status": "notifications_sent", "categories": []}
        
        for category_report in problematic_categories:
            category = category_report['category']
            
            # Check cooldown
            if not self.monitor.should_send_notification(category):
                logger.info(f"Skipping notification for {category} due to cooldown")
                continue
            
            category_results = {"category": category, "notifications": {}}
            
            # Send Slack notification
            if self.slack_notifier:
                slack_success = self.slack_notifier.send_alert([category_report])
                category_results["notifications"]["slack"] = slack_success
            
            # Send email notification
            if self.email_notifier:
                email_success = self.email_notifier.send_alert([category_report])
                category_results["notifications"]["email"] = email_success
            
            # Update notification timestamp
            self.monitor.update_notification_timestamp(category)
            
            results["categories"].append(category_results)
        
        return results

def load_config_from_env() -> NotificationConfig:
    """Load configuration from environment variables"""
    return NotificationConfig(
        # Slack settings
        slack_enabled=os.getenv('SLACK_ENABLED', 'false').lower() == 'true',
        slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL', ''),
        slack_channel=os.getenv('SLACK_CHANNEL', '#support-alerts'),
        
        # SMTP settings
        smtp_enabled=os.getenv('SMTP_ENABLED', 'false').lower() == 'true',
        smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_username=os.getenv('SMTP_USERNAME', ''),
        smtp_password=os.getenv('SMTP_PASSWORD', ''),
        admin_email=os.getenv('ADMIN_EMAIL', ''),
        
        # Monitoring thresholds
        min_tickets_for_analysis=int(os.getenv('MIN_TICKETS_FOR_ANALYSIS', '5')),
        satisfaction_threshold=float(os.getenv('SATISFACTION_THRESHOLD', '0.6')),
        volume_threshold=int(os.getenv('VOLUME_THRESHOLD', '10')),
        time_window_hours=int(os.getenv('TIME_WINDOW_HOURS', '24')),
        cooldown_hours=int(os.getenv('COOLDOWN_HOURS', '6'))
    )

def main():
    """Main function for running the notification system"""
    config = load_config_from_env()
    manager = NotificationManager(config)
    
    results = manager.check_and_notify()
    
    print(f"Notification check completed: {results['status']}")
    if 'categories' in results:
        for cat_result in results['categories']:
            print(f"Category: {cat_result['category']}")
            for notif_type, success in cat_result['notifications'].items():
                print(f"  {notif_type}: {'✅' if success else '❌'}")

if __name__ == "__main__":
    main()
