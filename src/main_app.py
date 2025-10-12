"""
Main Application with Anonymous Ticket Submission and Admin Interface
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
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
    from simple_auth import (
        init_session_state, admin_login_page, admin_logout, require_admin_auth,
        manual_review_form, get_ticket_status_badge, display_ticket_summary
    )
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all required modules are in the Python path.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Support System", 
    layout="wide",
    page_icon="🎫"
)

# Initialize session state
init_session_state()

# Main navigation
def main_navigation():
    """Main navigation between user and admin interfaces"""
    
    # Header with navigation
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🎫 AI Support System")
    
    with col2:
        if st.session_state.admin_authenticated:
            if st.button("👤 Admin Dashboard", use_container_width=True):
                st.session_state.current_page = "admin_dashboard"
                st.rerun()
        else:
            if st.button("🔐 Admin Login", use_container_width=True):
                st.session_state.current_page = "admin_login"
                st.rerun()
    
    with col3:
        if st.session_state.admin_authenticated:
            if st.button("🚪 Logout", use_container_width=True):
                admin_logout()
        else:
            if st.button("📝 Submit Ticket", use_container_width=True):
                st.session_state.current_page = "ticket_submission"
                st.rerun()

def anonymous_ticket_submission():
    """Anonymous ticket submission interface"""
    
    st.header("📝 Submit Support Ticket")
    st.write("Submit your support request anonymously. No registration required!")
    
    # Ticket submission form
    with st.form("ticket_form"):
        st.subheader("Describe Your Issue")
        
        ticket_content = st.text_area(
            "What can we help you with?",
            placeholder="Describe your issue in detail...",
            height=150,
            help="Be as specific as possible to get the best assistance"
        )
        
        # Optional: Category suggestion
        st.subheader("Category (Optional)")
        category_hint = st.selectbox(
            "What type of issue is this? (Optional - helps us route your ticket)",
            ["Not sure", "Extension Development", "Extension Installation", "Extension Issues", 
             "VS Code Problems", "API Questions", "General Question", "Bug Report"],
            help="This helps us categorize your ticket for faster resolution"
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Submit Ticket", use_container_width=True)
        
        if submitted:
            if ticket_content.strip():
                process_ticket_submission(ticket_content, category_hint)
            else:
                st.error("❌ Please describe your issue before submitting.")

def process_ticket_submission(ticket_content: str, category_hint: str = "Not sure"):
    """Process anonymous ticket submission"""
    
    with st.spinner("Processing your ticket..."):
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
            
            # Calculate confidence score (simplified)
            confidence_score = 0.8 if sol_source == "KB (retrieved)" else 0.6
            
            # Check if manual review is needed
            review_collector = st.session_state.review_collector
            review_result = review_collector.collect_review_data(
                ticket_id, ticket_content, solution, confidence_score
            )
            
            # Prepare ticket data
            ticket_data = {
                "ticket_id": ticket_id,
                "ticket_content": ticket_content,
                "ticket_cat": category,
                "ticket_by": "anonymous_user",
                "ticket_status": "pending_review" if review_result["needs_review"] else "open",
                "ticket_timestamp": datetime.now().isoformat(),
                "solution": solution,
                "category_hint": category_hint,
                "confidence_score": confidence_score,
                "needs_manual_review": review_result["needs_review"]
            }
            
            # Save to Google Sheets
            try:
                append_ticket(ticket_data)
                sheets_success = True
            except Exception as e:
                st.error(f"Failed to save to Google Sheets: {e}")
                sheets_success = False
            
            # Display results
            st.success("✅ Your ticket has been submitted successfully!")
            
            # Show ticket summary
            display_ticket_summary(ticket_data)
            
            # Handle manual review if needed
            if review_result["needs_review"]:
                st.divider()
                review_data = review_result["review_data"]
                
                # Show manual review form
                review_submitted = manual_review_form(review_data)
                
                if review_submitted:
                    # Update ticket status
                    try:
                        update_ticket_fields(ticket_id, {"ticket_status": "pending_review"})
                    except Exception as e:
                        st.warning(f"Could not update ticket status: {e}")
            
            # Show satisfaction rating
            st.divider()
            st.subheader("📊 How was your experience?")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("😊 Helpful", use_container_width=True):
                    log_satisfaction(ticket_id, True)
                    st.success("Thank you for your feedback!")
            
            with col2:
                if st.button("😐 Neutral", use_container_width=True):
                    log_satisfaction(ticket_id, None)
                    st.info("Thank you for your feedback!")
            
            with col3:
                if st.button("😞 Not Helpful", use_container_width=True):
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

@require_admin_auth
def admin_dashboard():
    """Admin dashboard interface"""
    
    st.header("👤 Admin Dashboard")
    
    # Admin navigation
    admin_tabs = st.tabs([
        "📊 Overview", 
        "🎫 Ticket Management", 
        "⏳ Manual Reviews", 
        "📈 Analytics", 
        "🔔 Notifications",
        "⚙️ Settings"
    ])
    
    with admin_tabs[0]:  # Overview
        admin_overview()
    
    with admin_tabs[1]:  # Ticket Management
        ticket_management()
    
    with admin_tabs[2]:  # Manual Reviews
        manual_review_management()
    
    with admin_tabs[3]:  # Analytics
        admin_analytics()
    
    with admin_tabs[4]:  # Notifications
        admin_notifications()
    
    with admin_tabs[5]:  # Settings
        admin_settings()

def admin_overview():
    """Admin overview dashboard"""
    
    st.subheader("📊 System Overview")
    
    # Load data
    try:
        worksheet = get_worksheet()
        tickets_df = pd.DataFrame(worksheet.get_all_records())
        
        if not tickets_df.empty:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_tickets = len(tickets_df)
                st.metric("Total Tickets", total_tickets)
            
            with col2:
                open_tickets = len(tickets_df[tickets_df['ticket_status'] == 'open'])
                st.metric("Open Tickets", open_tickets)
            
            with col3:
                pending_reviews = len(tickets_df[tickets_df['ticket_status'] == 'pending_review'])
                st.metric("Pending Reviews", pending_reviews)
            
            with col4:
                resolved_tickets = len(tickets_df[tickets_df['ticket_status'] == 'resolved'])
                st.metric("Resolved Tickets", resolved_tickets)
            
            # Recent tickets
            st.subheader("📋 Recent Tickets")
            recent_tickets = tickets_df.tail(10)
            
            for _, ticket in recent_tickets.iterrows():
                with st.expander(f"{ticket['ticket_id']} - {ticket['ticket_cat']}"):
                    st.write(f"**Status:** {get_ticket_status_badge(ticket['ticket_status'])}")
                    st.write(f"**Content:** {ticket['ticket_content'][:200]}...")
                    st.write(f"**Submitted:** {ticket['ticket_timestamp']}")
        
        else:
            st.info("No tickets found in the system.")
    
    except Exception as e:
        st.error(f"Error loading overview data: {e}")

def ticket_management():
    """Ticket management interface"""
    
    st.subheader("🎫 Ticket Management")
    
    try:
        worksheet = get_worksheet()
        tickets_df = pd.DataFrame(worksheet.get_all_records())
        
        if not tickets_df.empty:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "open", "pending_review", "resolved"])
            
            with col2:
                category_filter = st.selectbox("Filter by Category", ["All"] + list(tickets_df['ticket_cat'].unique()))
            
            with col3:
                search_term = st.text_input("Search tickets", placeholder="Search content...")
            
            # Apply filters
            filtered_df = tickets_df.copy()
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['ticket_status'] == status_filter]
            
            if category_filter != "All":
                filtered_df = filtered_df[filtered_df['ticket_cat'] == category_filter]
            
            if search_term:
                filtered_df = filtered_df[filtered_df['ticket_content'].str.contains(search_term, case=False, na=False)]
            
            # Display tickets
            st.write(f"Showing {len(filtered_df)} tickets")
            
            for _, ticket in filtered_df.iterrows():
                with st.expander(f"{ticket['ticket_id']} - {ticket['ticket_cat']} - {get_ticket_status_badge(ticket['ticket_status'])}"):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Content:** {ticket['ticket_content']}")
                        if ticket.get('solution'):
                            st.write(f"**Solution:** {ticket['solution']}")
                    
                    with col2:
                        st.write(f"**Status:** {get_ticket_status_badge(ticket['ticket_status'])}")
                        st.write(f"**Category:** {ticket['ticket_cat']}")
                        st.write(f"**Submitted:** {ticket['ticket_timestamp']}")
                        
                        # Status update buttons
                        if ticket['ticket_status'] != 'resolved':
                            if st.button(f"✅ Resolve", key=f"resolve_{ticket['ticket_id']}"):
                                try:
                                    update_ticket_fields(ticket['ticket_id'], {"ticket_status": "resolved"})
                                    st.success("Ticket resolved!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating ticket: {e}")
                        
                        if ticket['ticket_status'] == 'open':
                            if st.button(f"⏳ Mark for Review", key=f"review_{ticket['ticket_id']}"):
                                try:
                                    update_ticket_fields(ticket['ticket_id'], {"ticket_status": "pending_review"})
                                    st.success("Ticket marked for review!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating ticket: {e}")
        
        else:
            st.info("No tickets found.")
    
    except Exception as e:
        st.error(f"Error loading tickets: {e}")

def manual_review_management():
    """Manual review management interface"""
    
    st.subheader("⏳ Manual Review Management")
    
    review_collector = st.session_state.review_collector
    pending_reviews = review_collector.get_pending_reviews()
    
    if pending_reviews:
        st.write(f"Found {len(pending_reviews)} tickets pending manual review")
        
        for review in pending_reviews:
            with st.expander(f"Review {review['review_id'][:8]} - {review['ticket_id']}"):
                
                st.write(f"**Ticket ID:** {review['ticket_id']}")
                st.write(f"**Confidence Score:** {review['confidence_score']:.2f}")
                st.write(f"**Submitted:** {review['timestamp']}")
                
                st.write("**Ticket Content:**")
                st.write(review['ticket_content'])
                
                st.write("**Suggested Solution:**")
                st.write(review['suggested_solution'])
                
                if review.get('contact_preference'):
                    st.write(f"**Contact Preference:** {review['contact_preference']}")
                
                if review.get('additional_context'):
                    st.write("**Additional Context:**")
                    st.write(review['additional_context'])
                
                # Admin actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{review['review_id']}"):
                        review_collector.update_review_status(review['review_id'], "approved", "Approved by admin")
                        st.success("Review approved!")
                        st.rerun()
                
                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{review['review_id']}"):
                        review_collector.update_review_status(review['review_id'], "rejected", "Rejected by admin")
                        st.success("Review rejected!")
                        st.rerun()
                
                with col3:
                    admin_notes = st.text_area("Admin Notes", key=f"notes_{review['review_id']}", placeholder="Add notes...")
                    if st.button(f"📝 Add Notes", key=f"notes_btn_{review['review_id']}"):
                        if admin_notes:
                            review_collector.update_review_status(review['review_id'], "noted", admin_notes)
                            st.success("Notes added!")
                            st.rerun()
    
    else:
        st.success("🎉 No tickets pending manual review!")

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
    
    # Notification configuration
    st.subheader("⚙️ Notification Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Slack Configuration**")
        slack_enabled = st.checkbox("Enable Slack Notifications", value=False)
        slack_webhook = st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/services/...")
    
    with col2:
        st.write("**Email Configuration**")
        email_enabled = st.checkbox("Enable Email Notifications", value=False)
        admin_email = st.text_input("Admin Email", placeholder="admin@yourcompany.com")
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved! (Note: This is a demo - settings are not persisted)")

def admin_settings():
    """Admin settings interface"""
    
    st.subheader("⚙️ System Settings")
    
    # System information
    st.write("**System Information**")
    st.write(f"- Version: 1.0.0")
    st.write(f"- Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"- Admin Session: Active")
    
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
    
    # System maintenance
    st.subheader("🔧 System Maintenance")
    
    if st.button("🧹 Clean Old Sessions", use_container_width=True):
        st.info("Session cleanup would be implemented here")

# Main application logic
def main():
    """Main application entry point"""
    
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
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            🤖 AI-Powered Support System<br>
            Anonymous Ticket Submission • Admin Management
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()