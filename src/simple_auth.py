"""
Simplified Role-Based System
- Anonymous ticket submission (no auth required)
- Admin authentication for management
- Manual review workflow with minimal data collection
"""

import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
import uuid

class AdminUser:
    """Simple admin user class"""
    
    def __init__(self, username: str, password_hash: str, created_at: str = None):
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = None
    
    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AdminUser':
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            created_at=data.get("created_at"),
            last_login=data.get("last_login")
        )

class AdminManager:
    """Manages admin authentication"""
    
    def __init__(self, admins_file: str = "admins.json"):
        self.admins_file = Path(admins_file)
        self.admins: Dict[str, AdminUser] = {}
        self.sessions: Dict[str, Dict] = {}
        
        self._load_admins()
        self._create_default_admin()
    
    def _load_admins(self):
        """Load admins from file"""
        if self.admins_file.exists():
            try:
                with open(self.admins_file, 'r', encoding='utf-8') as f:
                    admins_data = json.load(f)
                    for admin_data in admins_data:
                        admin = AdminUser.from_dict(admin_data)
                        self.admins[admin.username] = admin
            except Exception as e:
                st.error(f"Error loading admins: {e}")
    
    def _save_admins(self):
        """Save admins to file"""
        try:
            admins_data = [admin.to_dict() for admin in self.admins.values()]
            with open(self.admins_file, 'w', encoding='utf-8') as f:
                json.dump(admins_data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving admins: {e}")
    
    def _create_default_admin(self):
        """Create default admin if none exists"""
        if not self.admins:
            default_password = "admin123"
            password_hash = hashlib.sha256(default_password.encode()).hexdigest()
            
            admin = AdminUser(
                username="admin",
                password_hash=password_hash
            )
            self.admins["admin"] = admin
            self._save_admins()
            st.info("🔑 Default admin created: username='admin', password='admin123'")
    
    def authenticate_admin(self, username: str, password: str) -> bool:
        """Authenticate admin"""
        if username not in self.admins:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.admins[username].password_hash == password_hash
    
    def create_session(self, username: str) -> str:
        """Create admin session"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=8)  # 8 hour session
        
        session_data = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        self.sessions[session_id] = session_data
        
        # Update last login
        self.admins[username].last_login = datetime.now().isoformat()
        self._save_admins()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            del self.sessions[session_id]
            return None
        
        return session
    
    def logout(self, session_id: str):
        """Logout admin"""
        if session_id in self.sessions:
            del self.sessions[session_id]

class ManualReviewCollector:
    """Handles manual review data collection"""
    
    def __init__(self, reviews_file: str = "manual_reviews.json"):
        self.reviews_file = Path(reviews_file)
        self.reviews: List[Dict] = []
        self._load_reviews()
    
    def _load_reviews(self):
        """Load manual reviews from file"""
        if self.reviews_file.exists():
            try:
                with open(self.reviews_file, 'r', encoding='utf-8') as f:
                    self.reviews = json.load(f)
            except Exception as e:
                st.error(f"Error loading manual reviews: {e}")
    
    def _save_reviews(self):
        """Save manual reviews to file"""
        try:
            with open(self.reviews_file, 'w', encoding='utf-8') as f:
                json.dump(self.reviews, f, indent=2)
        except Exception as e:
            st.error(f"Error saving manual reviews: {e}")
    
    def collect_review_data(self, ticket_id: str, ticket_content: str, 
                           suggested_solution: str, confidence_score: float) -> Dict:
        """Collect minimal data for manual review"""
        
        # Determine if manual review is needed
        needs_manual_review = (
            confidence_score < 0.5 or  # Low confidence
            "error" in ticket_content.lower() or
            "crash" in ticket_content.lower() or
            "not working" in ticket_content.lower()
        )
        
        if not needs_manual_review:
            return {"needs_review": False}
        
        # Collect minimal data
        review_data = {
            "review_id": str(uuid.uuid4()),
            "ticket_id": ticket_id,
            "ticket_content": ticket_content,
            "suggested_solution": suggested_solution,
            "confidence_score": confidence_score,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "contact_preference": None,
            "additional_context": None
        }
        
        self.reviews.append(review_data)
        self._save_reviews()
        
        return {
            "needs_review": True,
            "review_data": review_data
        }
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get all pending manual reviews"""
        return [review for review in self.reviews if review["status"] == "pending"]
    
    def update_review_status(self, review_id: str, status: str, admin_notes: str = ""):
        """Update review status"""
        for review in self.reviews:
            if review["review_id"] == review_id:
                review["status"] = status
                review["admin_notes"] = admin_notes
                review["resolved_at"] = datetime.now().isoformat()
                break
        self._save_reviews()

def init_session_state():
    """Initialize session state"""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'admin_session_id' not in st.session_state:
        st.session_state.admin_session_id = None
    if 'admin_manager' not in st.session_state:
        st.session_state.admin_manager = AdminManager()
    if 'review_collector' not in st.session_state:
        st.session_state.review_collector = ManualReviewCollector()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "ticket_submission"

def admin_login_page():
    """Admin login page"""
    st.title("🔐 Admin Login")
    
    admin_manager = st.session_state.admin_manager
    
    with st.form("admin_login"):
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter admin password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_clicked = st.form_submit_button("🔑 Login", use_container_width=True)
        
        with col2:
            back_clicked = st.form_submit_button("⬅️ Back to Tickets", use_container_width=True)
        
        if login_clicked:
            if username and password:
                if admin_manager.authenticate_admin(username, password):
                    # Create session
                    session_id = admin_manager.create_session(username)
                    
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_session_id = session_id
                    
                    st.success(f"✅ Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.error("❌ Please enter both username and password")
        
        if back_clicked:
            st.session_state.current_page = "ticket_submission"
            st.rerun()
    
    # Demo credentials
    st.info("""
    **Demo Admin Credentials:**
    - Username: `admin`
    - Password: `admin123`
    """)

def admin_logout():
    """Admin logout"""
    if st.session_state.admin_session_id:
        st.session_state.admin_manager.logout(st.session_state.admin_session_id)
    
    st.session_state.admin_authenticated = False
    st.session_state.admin_session_id = None
    st.rerun()

def require_admin_auth(func):
    """Decorator to require admin authentication"""
    def wrapper(*args, **kwargs):
        if not st.session_state.admin_authenticated:
            admin_login_page()
            return
        return func(*args, **kwargs)
    return wrapper

def manual_review_form(review_data: Dict):
    """Display manual review data collection form"""
    st.warning("⚠️ This ticket requires manual review for better assistance.")
    
    st.subheader("📋 Additional Information (Optional)")
    st.write("Help us provide better support by providing minimal additional context:")
    
    with st.form("manual_review_form"):
        contact_preference = st.selectbox(
            "How would you like us to contact you? (Optional)",
            ["No contact needed", "Email", "Phone", "In-app notification"],
            help="We will only contact you if absolutely necessary"
        )
        
        additional_context = st.text_area(
            "Additional Context (Optional)",
            placeholder="Any additional information that might help us assist you better...",
            help="This helps our support team understand your issue better"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit_review = st.form_submit_button("✅ Submit for Review", use_container_width=True)
        
        with col2:
            skip_review = st.form_submit_button("⏭️ Skip Review", use_container_width=True)
        
        if submit_review:
            # Update review data
            review_data["contact_preference"] = contact_preference
            review_data["additional_context"] = additional_context
            review_data["status"] = "submitted"
            
            st.success("✅ Your ticket has been submitted for manual review. We'll get back to you soon!")
            return True
        
        if skip_review:
            st.info("ℹ️ Ticket submitted without manual review. You'll receive an automated response.")
            return False
    
    return None

def get_ticket_status_badge(status: str) -> str:
    """Get status badge for ticket"""
    badges = {
        "open": "🟡 Open",
        "resolved": "✅ Resolved", 
        "pending_review": "⏳ Pending Review",
        "in_progress": "🔵 In Progress"
    }
    return badges.get(status, "❓ Unknown")

def display_ticket_summary(ticket_data: Dict):
    """Display ticket summary"""
    st.subheader("📋 Ticket Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ticket ID", ticket_data.get("ticket_id", "N/A"))
    
    with col2:
        st.metric("Category", ticket_data.get("category", "N/A"))
    
    with col3:
        st.metric("Status", get_ticket_status_badge(ticket_data.get("status", "open")))
    
    st.write("**Description:**")
    st.write(ticket_data.get("content", "No description provided"))
    
    if ticket_data.get("solution"):
        st.write("**Suggested Solution:**")
        st.write(ticket_data.get("solution", "No solution provided"))