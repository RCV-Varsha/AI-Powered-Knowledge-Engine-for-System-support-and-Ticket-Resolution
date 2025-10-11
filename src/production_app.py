"""
Production-Ready Role-Based Support System
- OTP-based admin authentication
- Working email notifications
- Google Sheets integration
- Professional UI design
"""

import streamlit as st
import pandas as pd
import json
import smtplib
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, List
import uuid
import plotly.express as px
import plotly.graph_objects as go

# Import existing modules
try:
    from sheets_client import append_ticket, update_ticket_fields, get_worksheet, find_ticket_row
    from resolver import MultiModelResolver, tavily_search
    from article_suggester import (
        suggest_articles, log_ticket_resolution, get_article_analytics, 
        get_content_gaps, generate_improvement_alerts, get_article_title
    )
    from tavily_client import TAVILY_AVAILABLE, TavilySearchClient, create_search_context
    from notification_system import NotificationManager, load_config_from_env
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all required modules are in the Python path.")
    st.stop()

# Configuration
ADMIN_NAME = "Chakra Varshini"
ADMIN_EMAIL = "chakravarshini395@gmail.com"
SYSTEM_NAME = "AI Support System"
DEVELOPER_NAME = "Chakra Varshini"

# Load configuration from environment variables
def load_config():
    """Load configuration from environment variables"""
    import os
    from dotenv import load_dotenv
    
    # Load .env file
    load_dotenv()
    
    return {
        "admin_name": os.getenv("ADMIN_NAME", ADMIN_NAME),
        "admin_email": os.getenv("ADMIN_EMAIL", ADMIN_EMAIL),
        "system_name": os.getenv("SYSTEM_NAME", SYSTEM_NAME),
        "developer_name": os.getenv("DEVELOPER_NAME", DEVELOPER_NAME),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_username": os.getenv("SMTP_USERNAME", ADMIN_EMAIL),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "smtp_sender_name": os.getenv("SMTP_SENDER_NAME", ADMIN_NAME)
    }

# Load configuration
CONFIG = load_config()

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": CONFIG["smtp_server"],
    "smtp_port": CONFIG["smtp_port"],
    "sender_email": CONFIG["smtp_username"],
    "sender_password": CONFIG["smtp_password"],
    "sender_name": CONFIG["smtp_sender_name"]
}

class OTPManager:
    """Manages OTP generation and verification"""
    
    def __init__(self, otp_file: str = "otp_sessions.json"):
        self.otp_file = Path(otp_file)
        self.otp_sessions: Dict[str, Dict] = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """Load OTP sessions from file"""
        if self.otp_file.exists():
            try:
                with open(self.otp_file, 'r', encoding='utf-8') as f:
                    self.otp_sessions = json.load(f)
            except Exception as e:
                st.error(f"Error loading OTP sessions: {e}")
    
    def _save_sessions(self):
        """Save OTP sessions to file"""
        try:
            with open(self.otp_file, 'w', encoding='utf-8') as f:
                json.dump(self.otp_sessions, f, indent=2)
        except Exception as e:
            st.error(f"Error saving OTP sessions: {e}")
    
    def generate_otp(self, email: str) -> str:
        """Generate and store OTP for email"""
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.now() + timedelta(minutes=10)  # 10 minute expiry
        
        self.otp_sessions[email] = {
            "otp": otp,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "attempts": 0,
            "verified": False
        }
        
        self._save_sessions()
        return otp
    
    def verify_otp(self, email: str, input_otp: str) -> bool:
        """Verify OTP for email"""
        if email not in self.otp_sessions:
            return False
        
        session = self.otp_sessions[email]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        # Check if expired
        if datetime.now() > expires_at:
            del self.otp_sessions[email]
            self._save_sessions()
            return False
        
        # Check attempts
        if session["attempts"] >= 3:
            del self.otp_sessions[email]
            self._save_sessions()
            return False
        
        # Verify OTP
        if session["otp"] == input_otp:
            session["verified"] = True
            session["verified_at"] = datetime.now().isoformat()
            self._save_sessions()
            return True
        else:
            session["attempts"] += 1
            self._save_sessions()
            return False
    
    def is_verified(self, email: str) -> bool:
        """Check if email is verified"""
        if email not in self.otp_sessions:
            return False
        
        session = self.otp_sessions[email]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            del self.otp_sessions[email]
            self._save_sessions()
            return False
        
        return session.get("verified", False)

class EmailService:
    """Handles email sending functionality"""
    
    def __init__(self):
        self.config = EMAIL_CONFIG
    
    def send_otp_email(self, email: str, otp: str) -> bool:
        """Send OTP email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = email
            msg['Subject'] = f"OTP for {CONFIG['system_name']} Admin Access"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        🔐 Admin Access OTP
                    </h2>
                    
                    <p>Hello {CONFIG['admin_name']},</p>
                    
                    <p>You have requested admin access to the <strong>{CONFIG['system_name']}</strong>.</p>
                    
                    <div style="background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #2c3e50;">Your OTP Code:</h3>
                        <div style="font-size: 32px; font-weight: bold; color: #e74c3c; letter-spacing: 5px; text-align: center; background-color: #fff; padding: 20px; border: 2px dashed #3498db; margin: 10px 0;">
                            {otp}
                        </div>
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>This OTP is valid for <strong>10 minutes</strong> only</li>
                        <li>Do not share this code with anyone</li>
                        <li>If you didn't request this, please ignore this email</li>
                    </ul>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666;">
                        This email was sent from {CONFIG['system_name']} by {CONFIG['developer_name']}<br>
                        If you have any questions, please contact the system administrator.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['sender_email'], self.config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(self.config['sender_email'], email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to send OTP email: {e}")
            return False
    
    def send_notification_email(self, subject: str, content: str, recipient_email: str = ADMIN_EMAIL) -> bool:
        """Send notification email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = recipient_email
            msg['Subject'] = f"{CONFIG['system_name']} - {subject}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        🔔 {CONFIG['system_name']} Notification
                    </h2>
                    
                    <p>Hello {CONFIG['admin_name']},</p>
                    
                    <div style="background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0;">
                        {content}
                    </div>
                    
                    <p>Please log in to the admin dashboard to review and take action.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666;">
                        This notification was sent from {CONFIG['system_name']} by {CONFIG['developer_name']}<br>
                        System: AI-Powered Support Platform
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['sender_email'], self.config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(self.config['sender_email'], recipient_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to send notification email: {e}")
            return False

class AdminSessionManager:
    """Manages admin sessions"""
    
    def __init__(self, sessions_file: str = "admin_sessions.json"):
        self.sessions_file = Path(sessions_file)
        self.sessions: Dict[str, Dict] = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from file"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
            except Exception as e:
                st.error(f"Error loading sessions: {e}")
    
    def _save_sessions(self):
        """Save sessions to file"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            st.error(f"Error saving sessions: {e}")
    
    def create_session(self, email: str) -> str:
        """Create new admin session"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=8)
        
        session_data = {
            "email": email,
            "name": ADMIN_NAME,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        self.sessions[session_id] = session_data
        self._save_sessions()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            del self.sessions[session_id]
            self._save_sessions()
            return None
        
        # Update last activity
        session["last_activity"] = datetime.now().isoformat()
        self._save_sessions()
        
        return session
    
    def logout(self, session_id: str):
        """Logout admin"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()

def init_session_state():
    """Initialize session state"""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'admin_session_id' not in st.session_state:
        st.session_state.admin_session_id = None
    if 'admin_email' not in st.session_state:
        st.session_state.admin_email = None
    if 'otp_manager' not in st.session_state:
        st.session_state.otp_manager = OTPManager()
    if 'email_service' not in st.session_state:
        st.session_state.email_service = EmailService()
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = AdminSessionManager()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "ticket_submission"

def admin_login_page():
    """OTP-based admin login page"""
    
    st.title("🔐 Admin Access")
    st.write(f"**System:** {CONFIG['system_name']}")
    st.write(f"**Administrator:** {CONFIG['admin_name']}")
    
    # Step 1: Email verification
    if not st.session_state.get('otp_sent', False):
        st.subheader("Step 1: Verify Email Address")
        
        with st.form("email_form"):
            email = st.text_input(
                "Admin Email", 
                value=CONFIG['admin_email'],
                disabled=True,
                help="This is the registered admin email"
            )
            
            send_otp = st.form_submit_button("📧 Send OTP", use_container_width=True)
            
            if send_otp:
                if email == CONFIG['admin_email']:
                    # Generate and send OTP
                    otp = st.session_state.otp_manager.generate_otp(email)
                    
                    # Send email
                    if st.session_state.email_service.send_otp_email(email, otp):
                        st.session_state.otp_sent = True
                        st.session_state.admin_email = email
                        st.success("✅ OTP sent successfully! Check your email.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to send OTP email. Please check email configuration.")
                else:
                    st.error("❌ Invalid email address.")
    
    # Step 2: OTP verification
    else:
        st.subheader("Step 2: Enter OTP Code")
        st.info(f"OTP sent to: {st.session_state.admin_email}")
        
        with st.form("otp_form"):
            otp_input = st.text_input(
                "Enter 6-digit OTP", 
                placeholder="123456",
                max_chars=6,
                help="Check your email for the OTP code"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                verify_otp = st.form_submit_button("✅ Verify OTP", use_container_width=True)
            
            with col2:
                resend_otp = st.form_submit_button("🔄 Resend OTP", use_container_width=True)
            
            if verify_otp:
                if len(otp_input) == 6 and otp_input.isdigit():
                    if st.session_state.otp_manager.verify_otp(st.session_state.admin_email, otp_input):
                        # Create session
                        session_id = st.session_state.session_manager.create_session(st.session_state.admin_email)
                        
                        st.session_state.admin_authenticated = True
                        st.session_state.admin_session_id = session_id
                        st.session_state.otp_sent = False
                        
                        st.success(f"✅ Welcome, {CONFIG['admin_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP. Please try again.")
                else:
                    st.error("❌ Please enter a valid 6-digit OTP.")
            
            if resend_otp:
                otp = st.session_state.otp_manager.generate_otp(st.session_state.admin_email)
                if st.session_state.email_service.send_otp_email(st.session_state.admin_email, otp):
                    st.success("✅ New OTP sent!")
                    st.rerun()
                else:
                    st.error("❌ Failed to resend OTP.")
        
        # Back button
        if st.button("⬅️ Back to Email", use_container_width=True):
            st.session_state.otp_sent = False
            st.rerun()
    
    # Back to main page
    if st.button("🏠 Back to Main Page", use_container_width=True):
        st.session_state.current_page = "ticket_submission"
        st.rerun()

def admin_logout():
    """Admin logout"""
    if st.session_state.admin_session_id:
        st.session_state.session_manager.logout(st.session_state.admin_session_id)
    
    st.session_state.admin_authenticated = False
    st.session_state.admin_session_id = None
    st.session_state.admin_email = None
    st.session_state.otp_sent = False
    st.rerun()

def require_admin_auth(func):
    """Decorator to require admin authentication"""
    def wrapper(*args, **kwargs):
        if not st.session_state.admin_authenticated:
            admin_login_page()
            return
        return func(*args, **kwargs)
    return wrapper

def main_navigation():
    """Main navigation with professional design"""
    
    # Custom CSS for professional look
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    .main-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    .admin-button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .admin-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .footer {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
        text-align: center;
        border-top: 3px solid #667eea;
    }
    .footer-text {
        color: #6c757d;
        font-size: 0.9rem;
        margin: 0;
    }
    .developer-credit {
        color: #667eea;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1 class="main-title">{CONFIG['system_name']}</h1>
        <p class="main-subtitle">Intelligent Support Platform • Developed by {CONFIG['developer_name']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "ticket_submission"
            st.rerun()
    
    with col2:
        if st.session_state.admin_authenticated:
            if st.button("👤 Admin Dashboard", use_container_width=True):
                st.session_state.current_page = "admin_dashboard"
                st.rerun()
        else:
            if st.button("🔐 Admin", use_container_width=True):
                st.session_state.current_page = "admin_login"
                st.rerun()
    
    with col3:
        if st.session_state.admin_authenticated:
            if st.button("🚪 Logout", use_container_width=True):
                admin_logout()

def anonymous_ticket_submission():
    """Professional anonymous ticket submission interface"""
    
    st.header("📝 Submit Support Request")
    st.write("Get instant help with your technical questions. No registration required!")
    
    # Ticket submission form
    with st.form("ticket_form", clear_on_submit=True):
        st.subheader("Describe Your Issue")
        
        ticket_content = st.text_area(
            "What can we help you with?",
            placeholder="Please describe your issue in detail. The more specific you are, the better we can assist you...",
            height=150,
            help="Include error messages, steps to reproduce, and any relevant context"
        )
        
        # Category suggestion
        st.subheader("Category Selection")
        category_hint = st.selectbox(
            "What type of issue is this?",
            ["Not sure", "Extension Development", "Extension Installation", "Extension Issues", 
             "VS Code Problems", "API Questions", "General Question", "Bug Report", "Feature Request"],
            help="This helps us route your ticket for faster resolution"
        )
        
        # Submit button
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True, type="primary")
        
        with col2:
            clear_form = st.form_submit_button("🗑️ Clear Form", use_container_width=True)
        
        if submitted:
            if ticket_content.strip():
                process_ticket_submission(ticket_content, category_hint)
            else:
                st.error("❌ Please describe your issue before submitting.")

def process_ticket_submission(ticket_content: str, category_hint: str = "Not sure"):
    """Process anonymous ticket submission with proper error handling"""
    
    with st.spinner("🤖 Processing your request..."):
        try:
            # Generate ticket ID
            ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
            
            # Get resolver
            resolver = MultiModelResolver(enable_web_search=st.session_state.get('web_search_enabled', False))
            
            # Categorize ticket
            category, cat_source = resolver.safe_categorize_ticket(ticket_content)
            
            # Get article suggestions
            suggestions = suggest_articles(ticket_content)
            
            # Generate solution
            kb_context = "\n".join([doc.page_content[:300] for doc in suggestions])
            solution, sol_source = resolver.safe_generate_solution(
                ticket_content,
                category,
                kb_context,
                use_web_search=st.session_state.get('web_search_enabled', False)
            )
            
            # Calculate confidence score
            confidence_score = 0.8 if sol_source == "KB (retrieved)" else 0.6
            
            # Prepare ticket data
            ticket_data = {
                "ticket_id": ticket_id,
                "ticket_content": ticket_content,
                "ticket_cat": category,
                "ticket_by": "anonymous_user",
                "ticket_status": "open",
                "ticket_timestamp": datetime.now().isoformat(),
                "solution": solution,
                "category_hint": category_hint,
                "confidence_score": confidence_score,
                "needs_manual_review": confidence_score < 0.5
            }
            
            # Save to Google Sheets
            try:
                append_ticket(ticket_data)
                sheets_success = True
            except Exception as e:
                st.error(f"Failed to save to Google Sheets: {e}")
                sheets_success = False
            
            # Display results
            st.success("✅ Your request has been submitted successfully!")
            
            # Show ticket summary
            display_ticket_summary(ticket_data)
            
            # Check if manual review is needed
            if confidence_score < 0.5 or any(keyword in ticket_content.lower() for keyword in ["error", "crash", "not working", "broken"]):
                st.warning("⚠️ This request may require manual review for better assistance.")
                
                # Send notification to admin
                try:
                    notification_content = f"""
                    <h3>New Ticket Requiring Manual Review</h3>
                    <p><strong>Ticket ID:</strong> {ticket_id}</p>
                    <p><strong>Category:</strong> {category}</p>
                    <p><strong>Issue:</strong> {ticket_content[:200]}...</p>
                    <p><strong>Confidence Score:</strong> {confidence_score:.2f}</p>
                    <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>System:</strong> {CONFIG['system_name']}</p>
                    """
                    
                    if st.session_state.email_service.send_notification_email(
                        "Manual Review Required", 
                        notification_content
                    ):
                        st.info("📧 Admin has been notified for manual review.")
                except Exception as e:
                    st.warning(f"Could not send notification: {e}")
            
            # Satisfaction rating (outside of form)
            st.divider()
            st.subheader("📊 How was your experience?")
            
            # Store ticket data for satisfaction rating
            st.session_state.current_ticket_id = ticket_id
            st.session_state.current_ticket_solution = solution
            
            # Satisfaction buttons (outside form)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("😊 Helpful", use_container_width=True, key="helpful_btn"):
                    log_satisfaction(ticket_id, True)
                    st.success("Thank you for your feedback!")
            
            with col2:
                if st.button("😐 Neutral", use_container_width=True, key="neutral_btn"):
                    log_satisfaction(ticket_id, None)
                    st.info("Thank you for your feedback!")
            
            with col3:
                if st.button("😞 Not Helpful", use_container_width=True, key="not_helpful_btn"):
                    log_satisfaction(ticket_id, False)
                    st.warning("We're sorry the response wasn't helpful. We'll work to improve!")
            
        except Exception as e:
            st.error(f"Error processing ticket: {e}")
            st.exception(e)

def log_satisfaction(ticket_id: str, satisfied: bool):
    """Log user satisfaction"""
    try:
        log_ticket_resolution(
            ticket_id=ticket_id,
            ticket_content="",  # Not needed for satisfaction logging
            category="",
            solution="",
            suggested_articles=[],
            user_satisfied=satisfied
        )
    except Exception as e:
        st.error(f"Error logging satisfaction: {e}")

def display_ticket_summary(ticket_data: Dict):
    """Display professional ticket summary"""
    
    st.subheader("📋 Request Summary")
    
    # Create columns for better layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Request ID", ticket_data.get("ticket_id", "N/A"))
    
    with col2:
        st.metric("Category", ticket_data.get("ticket_cat", "N/A"))
    
    with col3:
        status_badge = "🟡 Open" if ticket_data.get("ticket_status") == "open" else "✅ Resolved"
        st.metric("Status", status_badge)
    
    # Description section
    st.write("**Description:**")
    st.info(ticket_data.get("ticket_content", "No description provided"))
    
    # Solution section
    if ticket_data.get("solution"):
        st.write("**Suggested Solution:**")
        st.success(ticket_data.get("solution", "No solution provided"))

@require_admin_auth
def admin_dashboard():
    """Professional admin dashboard"""
    
    st.header(f"👤 Admin Dashboard - {CONFIG['admin_name']}")
    
    # Admin navigation tabs
    admin_tabs = st.tabs([
        "📊 Overview", 
        "🎫 Ticket Management", 
        "📈 Analytics", 
        "🔔 Notifications",
        "⚙️ Settings"
    ])
    
    with admin_tabs[0]:  # Overview
        admin_overview()
    
    with admin_tabs[1]:  # Ticket Management
        ticket_management()
    
    with admin_tabs[2]:  # Analytics
        admin_analytics()
    
    with admin_tabs[3]:  # Notifications
        admin_notifications()
    
    with admin_tabs[4]:  # Settings
        admin_settings()

def admin_overview():
    """Admin overview dashboard with Google Sheets integration"""
    
    st.subheader("📊 System Overview")
    
    try:
        # Get data from Google Sheets
        worksheet = get_worksheet()
        tickets_data = worksheet.get_all_records()
        
        if tickets_data:
            tickets_df = pd.DataFrame(tickets_data)
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_tickets = len(tickets_df)
                st.metric("Total Requests", total_tickets)
            
            with col2:
                open_tickets = len(tickets_df[tickets_df['ticket_status'] == 'open'])
                st.metric("Open Requests", open_tickets)
            
            with col3:
                resolved_tickets = len(tickets_df[tickets_df['ticket_status'] == 'resolved'])
                st.metric("Resolved Requests", resolved_tickets)
            
            with col4:
                # Calculate resolution rate
                if total_tickets > 0:
                    resolution_rate = (resolved_tickets / total_tickets) * 100
                    st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
                else:
                    st.metric("Resolution Rate", "0%")
            
            # Recent tickets
            st.subheader("📋 Recent Requests")
            
            # Sort by timestamp and get recent 10
            if 'ticket_timestamp' in tickets_df.columns:
                tickets_df['ticket_timestamp'] = pd.to_datetime(tickets_df['ticket_timestamp'], errors='coerce')
                recent_tickets = tickets_df.sort_values('ticket_timestamp', ascending=False).head(10)
            else:
                recent_tickets = tickets_df.tail(10)
            
            for _, ticket in recent_tickets.iterrows():
                with st.expander(f"{ticket.get('ticket_id', 'N/A')} - {ticket.get('ticket_cat', 'N/A')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Description:** {ticket.get('ticket_content', 'No description')[:200]}...")
                        if ticket.get('solution'):
                            st.write(f"**Solution:** {ticket.get('solution', 'No solution')[:200]}...")
                    
                    with col2:
                        status = ticket.get('ticket_status', 'open')
                        status_badge = "🟡 Open" if status == "open" else "✅ Resolved"
                        st.write(f"**Status:** {status_badge}")
                        st.write(f"**Category:** {ticket.get('ticket_cat', 'N/A')}")
                        st.write(f"**Submitted:** {ticket.get('ticket_timestamp', 'N/A')}")
        
        else:
            st.info("No requests found in the system.")
    
    except Exception as e:
        st.error(f"Error loading overview data: {e}")
        st.write("Make sure Google Sheets integration is properly configured.")

def ticket_management():
    """Professional ticket management with Google Sheets integration"""
    
    st.subheader("🎫 Request Management")
    
    try:
        # Get data from Google Sheets
        worksheet = get_worksheet()
        tickets_data = worksheet.get_all_records()
        
        if tickets_data:
            tickets_df = pd.DataFrame(tickets_data)
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "open", "resolved"])
            
            with col2:
                category_filter = st.selectbox("Filter by Category", ["All"] + list(tickets_df['ticket_cat'].unique()))
            
            with col3:
                search_term = st.text_input("Search requests", placeholder="Search content...")
            
            # Apply filters
            filtered_df = tickets_df.copy()
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['ticket_status'] == status_filter]
            
            if category_filter != "All":
                filtered_df = filtered_df[filtered_df['ticket_cat'] == category_filter]
            
            if search_term:
                filtered_df = filtered_df[filtered_df['ticket_content'].str.contains(search_term, case=False, na=False)]
            
            # Display tickets
            st.write(f"Showing {len(filtered_df)} requests")
            
            for _, ticket in filtered_df.iterrows():
                with st.expander(f"{ticket.get('ticket_id', 'N/A')} - {ticket.get('ticket_cat', 'N/A')} - {get_ticket_status_badge(ticket.get('ticket_status', 'open'))}"):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Description:** {ticket.get('ticket_content', 'No description')}")
                        if ticket.get('solution'):
                            st.write(f"**Solution:** {ticket.get('solution', 'No solution')}")
                    
                    with col2:
                        st.write(f"**Status:** {get_ticket_status_badge(ticket.get('ticket_status', 'open'))}")
                        st.write(f"**Category:** {ticket.get('ticket_cat', 'N/A')}")
                        st.write(f"**Submitted:** {ticket.get('ticket_timestamp', 'N/A')}")
                        
                        # Status update buttons
                        if ticket.get('ticket_status') != 'resolved':
                            if st.button(f"✅ Mark Resolved", key=f"resolve_{ticket.get('ticket_id')}"):
                                try:
                                    update_ticket_fields(ticket.get('ticket_id'), {"ticket_status": "resolved"})
                                    st.success("Request marked as resolved!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating request: {e}")
        
        else:
            st.info("No requests found.")
    
    except Exception as e:
        st.error(f"Error loading requests: {e}")
        st.write("Make sure Google Sheets integration is properly configured.")

def get_ticket_status_badge(status: str) -> str:
    """Get status badge for ticket"""
    badges = {
        "open": "🟡 Open",
        "resolved": "✅ Resolved", 
        "pending_review": "⏳ Pending Review",
        "in_progress": "🔵 In Progress"
    }
    return badges.get(status, "❓ Unknown")

def admin_analytics():
    """Admin analytics interface"""
    
    st.subheader("📈 System Analytics")
    
    try:
        analytics = get_article_analytics()
        
        if analytics['total_suggestions'] > 0:
            # Analytics charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Article Performance")
                
                if analytics['satisfaction_by_article']:
                    article_data = []
                    for article, stats in analytics['satisfaction_by_article'].items():
                        article_data.append({
                            'Article': article,
                            'Satisfaction Rate': stats['satisfied'] / stats['total'] if stats['total'] > 0 else 0,
                            'Total Uses': stats['total']
                        })
                    
                    if article_data:
                        df = pd.DataFrame(article_data)
                        fig = px.bar(df, x='Article', y='Satisfaction Rate', title='Article Satisfaction Rates')
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Usage Statistics")
                
                usage_data = {
                    'Metric': ['Total Suggestions', 'Most Used Articles', 'Low Satisfaction Articles'],
                    'Count': [
                        analytics['total_suggestions'],
                        len(analytics['most_suggested_articles']),
                        len(analytics['articles_needing_improvement'])
                    ]
                }
                
                df = pd.DataFrame(usage_data)
                fig = px.pie(df, values='Count', names='Metric', title='System Usage Overview')
                st.plotly_chart(fig, use_container_width=True)
            
            # Articles needing improvement
            if analytics['articles_needing_improvement']:
                st.subheader("⚠️ Articles Needing Improvement")
                
                for article in analytics['articles_needing_improvement']:
                    st.write(f"**{article['article']}** - Satisfaction: {article['satisfaction_rate']:.1%} ({article['total_uses']} uses)")
        
        else:
            st.info("No analytics data available yet.")
    
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def admin_notifications():
    """Admin notifications interface"""
    
    st.subheader("🔔 Notification Management")
    
    # Manual notification check
    if st.button("🚀 Run Category Analysis", use_container_width=True):
        with st.spinner("Analyzing category performance..."):
            try:
                config = load_config_from_env()
                manager = NotificationManager(config)
                results = manager.check_and_notify()
                
                st.success("Analysis completed!")
                
                if 'categories' in results:
                    for cat_result in results['categories']:
                        st.write(f"**{cat_result['category']}:**")
                        for notif_type, success in cat_result['notifications'].items():
                            st.write(f"  - {notif_type}: {'✅ Success' if success else '❌ Failed'}")
                
            except Exception as e:
                st.error(f"Error running analysis: {e}")
    
    # Test email notification
    st.subheader("📧 Test Email Notification")
    
    if st.button("📤 Send Test Email", use_container_width=True):
        with st.spinner("Sending test email..."):
            try:
                test_content = f"""
                <h3>Test Notification</h3>
                <p>This is a test email from the {CONFIG['system_name']}.</p>
                <p><strong>Admin:</strong> {CONFIG['admin_name']}</p>
                <p><strong>System:</strong> AI-Powered Support Platform</p>
                <p><strong>Developer:</strong> {CONFIG['developer_name']}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                """
                
                if st.session_state.email_service.send_notification_email("Test Notification", test_content):
                    st.success("✅ Test email sent successfully!")
                else:
                    st.error("❌ Failed to send test email.")
            except Exception as e:
                st.error(f"Error sending test email: {e}")

def admin_settings():
    """Admin settings interface"""
    
    st.subheader("⚙️ System Settings")
    
    # System information
    st.write("**System Information**")
    st.write(f"- System Name: {CONFIG['system_name']}")
    st.write(f"- Administrator: {CONFIG['admin_name']}")
    st.write(f"- Admin Email: {CONFIG['admin_email']}")
    st.write(f"- Developer: {CONFIG['developer_name']}")
    st.write(f"- Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"- Admin Session: Active")
    
    # Email configuration
    st.subheader("📧 Email Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**SMTP Settings**")
        st.write(f"- Server: {EMAIL_CONFIG['smtp_server']}")
        st.write(f"- Port: {EMAIL_CONFIG['smtp_port']}")
        st.write(f"- Sender: {EMAIL_CONFIG['sender_email']}")
    
    with col2:
        st.write("**Notification Settings**")
        st.write("- OTP emails: Enabled")
        st.write("- Admin notifications: Enabled")
        st.write("- Manual review alerts: Enabled")
    
    # Data management
    st.subheader("🗄️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export All Data", use_container_width=True):
            st.info("Export functionality would be implemented here")
    
    with col2:
        if st.button("🔄 Refresh Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared!")
            st.rerun()

def professional_footer():
    """Professional footer with branding"""
    
    st.markdown("""
    <div class="footer">
        <p class="footer-text">
            🤖 <strong>{SYSTEM_NAME}</strong> • Intelligent Support Platform<br>
            Developed with ❤️ by <span class="developer-credit">{DEVELOPER_NAME}</span><br>
            Administrator: {ADMIN_NAME} • Email: {ADMIN_EMAIL}
        </p>
    </div>
    """.format(
        SYSTEM_NAME=CONFIG['system_name'],
        DEVELOPER_NAME=CONFIG['developer_name'],
        ADMIN_NAME=CONFIG['admin_name'],
        ADMIN_EMAIL=CONFIG['admin_email']
    ), unsafe_allow_html=True)

# Main application logic
def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title=f"{CONFIG['system_name']} - {CONFIG['developer_name']}",
        layout="wide",
        page_icon="🎫",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    init_session_state()
    
    # Main navigation
    main_navigation()
    
    # Route to appropriate page
    current_page = st.session_state.current_page
    
    if current_page == "ticket_submission":
        anonymous_ticket_submission()
    
    elif current_page == "admin_login":
        admin_login_page()
    
    elif current_page == "admin_dashboard":
        admin_dashboard()
    
    else:
        # Default to ticket submission
        st.session_state.current_page = "ticket_submission"
        anonymous_ticket_submission()
    
    # Professional footer
    professional_footer()

if __name__ == "__main__":
    main()
