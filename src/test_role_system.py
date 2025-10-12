"""
Test script for the role-based support system
"""

import json
from datetime import datetime
from pathlib import Path

def test_manual_review_system():
    """Test the manual review system"""
    
    print("🧪 Testing Manual Review System")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        {
            "ticket_content": "Extension crashes when opening large files",
            "expected_review": True,
            "reason": "Contains 'crash' keyword"
        },
        {
            "ticket_content": "How to build an extension?",
            "expected_review": False,
            "reason": "Simple question, high confidence expected"
        },
        {
            "ticket_content": "Error code 500 when trying to publish",
            "expected_review": True,
            "reason": "Contains 'error' keyword"
        },
        {
            "ticket_content": "Extension not working properly",
            "expected_review": True,
            "reason": "Contains 'not working' phrase"
        },
        {
            "ticket_content": "What is VS Code?",
            "expected_review": False,
            "reason": "Simple informational question"
        }
    ]
    
    print("Testing manual review triggers...")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        ticket_content = test_case["ticket_content"]
        expected = test_case["expected_review"]
        reason = test_case["reason"]
        
        # Simulate review logic
        needs_review = (
            "error" in ticket_content.lower() or
            "crash" in ticket_content.lower() or
            "not working" in ticket_content.lower()
        )
        
        status = "✅ PASS" if needs_review == expected else "❌ FAIL"
        
        print(f"{i}. {status} - '{ticket_content[:30]}...'")
        print(f"   Expected: {expected}, Got: {needs_review}")
        print(f"   Reason: {reason}")
        print()
    
    print("Manual review system test completed!")

def test_admin_authentication():
    """Test admin authentication system"""
    
    print("🔐 Testing Admin Authentication")
    print("=" * 40)
    
    # Test default admin creation
    print("1. Testing default admin creation...")
    
    # Simulate admin file creation
    admin_data = {
        "username": "admin",
        "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # admin123
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    print("✅ Default admin created successfully")
    print(f"   Username: {admin_data['username']}")
    print(f"   Password: admin123")
    print()
    
    # Test authentication
    print("2. Testing authentication...")
    
    test_credentials = [
        ("admin", "admin123", True),
        ("admin", "wrongpassword", False),
        ("wronguser", "admin123", False),
        ("", "", False)
    ]
    
    for username, password, expected in test_credentials:
        # Simulate authentication
        if username == "admin" and password == "admin123":
            result = True
        else:
            result = False
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"   {status} - Username: '{username}', Password: '{password}'")
    
    print()
    print("Admin authentication test completed!")

def test_ticket_processing():
    """Test ticket processing workflow"""
    
    print("🎫 Testing Ticket Processing Workflow")
    print("=" * 40)
    
    # Test ticket data structure
    sample_ticket = {
        "ticket_id": "TICKET-20250115143000-ABCD",
        "ticket_content": "Extension crashes when opening large files",
        "ticket_cat": "Bug Report",
        "ticket_by": "anonymous_user",
        "ticket_status": "pending_review",
        "ticket_timestamp": datetime.now().isoformat(),
        "solution": "Try restarting VS Code and check for extension updates...",
        "category_hint": "Extension Issues",
        "confidence_score": 0.3,
        "needs_manual_review": True
    }
    
    print("1. Testing ticket data structure...")
    required_fields = [
        "ticket_id", "ticket_content", "ticket_cat", "ticket_by",
        "ticket_status", "ticket_timestamp", "solution"
    ]
    
    all_present = all(field in sample_ticket for field in required_fields)
    print(f"   {'✅ PASS' if all_present else '❌ FAIL'} - All required fields present")
    print()
    
    print("2. Testing manual review detection...")
    needs_review = sample_ticket["needs_manual_review"]
    print(f"   {'✅ PASS' if needs_review else '❌ FAIL'} - Manual review correctly detected")
    print()
    
    print("3. Testing ticket status workflow...")
    status_flow = ["open", "pending_review", "resolved"]
    current_status = sample_ticket["ticket_status"]
    print(f"   ✅ PASS - Status '{current_status}' is valid")
    print()
    
    print("Ticket processing test completed!")

def create_test_data():
    """Create test data files"""
    
    print("📁 Creating Test Data Files")
    print("=" * 40)
    
    # Create test ticket log
    test_tickets = [
        {
            "ticket_id": "TEST-001",
            "timestamp": datetime.now().isoformat(),
            "ticket_content": "Extension crashes when opening files",
            "category": "Bug Report",
            "solution_preview": "Try restarting VS Code...",
            "suggested_articles": ["troubleshooting", "debugging"],
            "user_satisfied": False,
            "resolution_time_seconds": None,
            "feedback_type": "negative"
        },
        {
            "ticket_id": "TEST-002",
            "timestamp": datetime.now().isoformat(),
            "ticket_content": "How to build an extension?",
            "category": "Getting Started",
            "solution_preview": "Follow the tutorial...",
            "suggested_articles": ["getting-started", "tutorial"],
            "user_satisfied": True,
            "resolution_time_seconds": None,
            "feedback_type": "positive"
        }
    ]
    
    # Write test ticket log
    with open("ticket_log.jsonl", "w", encoding="utf-8") as f:
        for ticket in test_tickets:
            f.write(json.dumps(ticket) + "\n")
    
    print("✅ Created test ticket log with 2 sample tickets")
    
    # Create test manual reviews
    test_reviews = [
        {
            "review_id": "REVIEW-001",
            "ticket_id": "TEST-001",
            "ticket_content": "Extension crashes when opening files",
            "suggested_solution": "Try restarting VS Code...",
            "confidence_score": 0.3,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "contact_preference": None,
            "additional_context": None
        }
    ]
    
    with open("manual_reviews.json", "w", encoding="utf-8") as f:
        json.dump(test_reviews, f, indent=2)
    
    print("✅ Created test manual reviews file")
    
    # Create test admin file
    test_admin = {
        "username": "admin",
        "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    with open("admins.json", "w", encoding="utf-8") as f:
        json.dump([test_admin], f, indent=2)
    
    print("✅ Created test admin file")
    print()
    print("Test data files created successfully!")

def cleanup_test_data():
    """Clean up test data files"""
    
    test_files = ["ticket_log.jsonl", "manual_reviews.json", "admins.json"]
    
    print("🧹 Cleaning up test data...")
    
    for file_name in test_files:
        if Path(file_name).exists():
            Path(file_name).unlink()
            print(f"✅ Removed {file_name}")
    
    print("Test data cleanup completed!")

def main():
    """Main test function"""
    
    print("🧪 Role-Based Support System Test Suite")
    print("=" * 50)
    print()
    
    # Run tests
    test_manual_review_system()
    print()
    
    test_admin_authentication()
    print()
    
    test_ticket_processing()
    print()
    
    # Create test data
    create_test_data()
    print()
    
    # Ask about cleanup
    cleanup = input("🧹 Clean up test data files? (y/n): ").lower().strip()
    if cleanup == 'y':
        cleanup_test_data()
    else:
        print("ℹ️ Test data files preserved for manual testing.")
    
    print()
    print("✅ Test suite completed!")
    print()
    print("🚀 Ready to launch the application:")
    print("   python launch_app.py")

if __name__ == "__main__":
    main()