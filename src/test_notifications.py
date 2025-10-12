"""
Test script for notification system
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def create_test_ticket_log():
    """Create test ticket log data for testing the notification system"""
    
    # Create test data with some problematic categories
    test_tickets = [
        {
            "ticket_id": "TEST-001",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "ticket_content": "Extension crashes when opening files",
            "category": "general_query",
            "solution_preview": "Try restarting VS Code...",
            "suggested_articles": ["troubleshooting", "debugging"],
            "user_satisfied": False,
            "resolution_time_seconds": None,
            "feedback_type": "negative"
        },
        {
            "ticket_id": "TEST-002", 
            "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
            "ticket_content": "How to build an extension?",
            "category": "general_query",
            "solution_preview": "Follow the tutorial...",
            "suggested_articles": ["getting-started", "tutorial"],
            "user_satisfied": False,
            "resolution_time_seconds": None,
            "feedback_type": "negative"
        },
        {
            "ticket_id": "TEST-003",
            "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
            "ticket_content": "Extension not working properly",
            "category": "general_query", 
            "solution_preview": "Check your configuration...",
            "suggested_articles": ["configuration", "troubleshooting"],
            "user_satisfied": False,
            "resolution_time_seconds": None,
            "feedback_type": "negative"
        },
        {
            "ticket_id": "TEST-004",
            "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
            "ticket_content": "Need help with extension development",
            "category": "general_query",
            "solution_preview": "Here's a comprehensive guide...",
            "suggested_articles": ["development", "api"],
            "user_satisfied": True,
            "resolution_time_seconds": None,
            "feedback_type": "positive"
        },
        {
            "ticket_id": "TEST-005",
            "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
            "ticket_content": "Extension installation failed",
            "category": "general_query",
            "solution_preview": "Try these steps...",
            "suggested_articles": ["installation", "troubleshooting"],
            "user_satisfied": False,
            "resolution_time_seconds": None,
            "feedback_type": "negative"
        },
        # Add some good performing categories for comparison
        {
            "ticket_id": "TEST-006",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "ticket_content": "How to publish extension?",
            "category": "publishing",
            "solution_preview": "Use vsce command...",
            "suggested_articles": ["publishing", "marketplace"],
            "user_satisfied": True,
            "resolution_time_seconds": None,
            "feedback_type": "positive"
        },
        {
            "ticket_id": "TEST-007",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "ticket_content": "Extension marketplace submission",
            "category": "publishing",
            "solution_preview": "Follow marketplace guidelines...",
            "suggested_articles": ["marketplace", "guidelines"],
            "user_satisfied": True,
            "resolution_time_seconds": None,
            "feedback_type": "positive"
        },
        {
            "ticket_id": "TEST-008",
            "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
            "ticket_content": "vsce publish command not working",
            "category": "publishing",
            "solution_preview": "Check your token...",
            "suggested_articles": ["vsce", "authentication"],
            "user_satisfied": True,
            "resolution_time_seconds": None,
            "feedback_type": "positive"
        }
    ]
    
    # Write test data to ticket log
    log_path = Path("ticket_log.jsonl")
    
    # Backup existing log if it exists
    if log_path.exists():
        backup_path = Path("ticket_log_backup.jsonl")
        log_path.rename(backup_path)
        print(f"📁 Backed up existing log to {backup_path}")
    
    # Write test data
    with open(log_path, 'w', encoding='utf-8') as f:
        for ticket in test_tickets:
            f.write(json.dumps(ticket) + '\n')
    
    print(f"✅ Created test ticket log with {len(test_tickets)} tickets")
    print("📊 Test data includes:")
    print("   - 5 tickets in 'general_query' category (4 unsatisfied, 1 satisfied)")
    print("   - 3 tickets in 'publishing' category (all satisfied)")
    print("   - This should trigger alerts for 'general_query' category")

def test_notification_system():
    """Test the notification system with test data"""
    
    print("🧪 Testing Notification System...")
    print()
    
    try:
        from notification_system import NotificationManager, NotificationConfig
        
        # Create test configuration
        config = NotificationConfig(
            slack_enabled=False,  # Disable actual notifications for test
            smtp_enabled=False,
            min_tickets_for_analysis=3,
            satisfaction_threshold=0.6,
            volume_threshold=5,
            time_window_hours=24,
            cooldown_hours=1
        )
        
        manager = NotificationManager(config)
        
        # Run analysis
        print("🔍 Analyzing category performance...")
        category_stats = manager.monitor.analyze_category_performance()
        
        if not category_stats:
            print("❌ No category data found")
            return
        
        print(f"📈 Found {len(category_stats)} categories with data:")
        for category, stats in category_stats.items():
            print(f"   - {category}: {stats['total_tickets']} tickets, {stats['satisfaction_rate']:.1%} satisfaction")
        
        print()
        print("🚨 Identifying problematic categories...")
        problematic_categories = manager.monitor.identify_problematic_categories(category_stats)
        
        if problematic_categories:
            print(f"⚠️  Found {len(problematic_categories)} problematic categories:")
            for cat_report in problematic_categories:
                category = cat_report['category']
                stats = cat_report['stats']
                issues = cat_report['issues']
                priority = cat_report['priority']
                
                print(f"\n🔴 {category.upper()} ({priority.upper()} PRIORITY)")
                print(f"   📊 Satisfaction: {stats['satisfaction_rate']:.1%} ({stats['satisfied_tickets']}/{stats['total_tickets']})")
                print(f"   📈 Volume: {stats['total_tickets']} tickets")
                
                for issue in issues:
                    severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡"
                    print(f"   {severity_emoji} {issue['message']}")
        else:
            print("✅ No problematic categories found")
        
        print()
        print("🎯 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def cleanup_test_data():
    """Clean up test data"""
    log_path = Path("ticket_log.jsonl")
    backup_path = Path("ticket_log_backup.jsonl")
    
    if backup_path.exists():
        log_path.unlink()  # Remove test data
        backup_path.rename(log_path)  # Restore original
        print("🧹 Cleaned up test data and restored original log")
    else:
        print("ℹ️  No backup found to restore")

def main():
    """Main test function"""
    print("🧪 Notification System Test Suite")
    print("=" * 50)
    print()
    
    # Create test data
    create_test_ticket_log()
    print()
    
    # Test the system
    test_notification_system()
    print()
    
    # Ask if user wants to clean up
    cleanup = input("🧹 Clean up test data? (y/n): ").lower().strip()
    if cleanup == 'y':
        cleanup_test_data()
    else:
        print("ℹ️  Test data preserved. You can run the dashboard to see the results.")
    
    print()
    print("✅ Test suite completed!")

if __name__ == "__main__":
    main()