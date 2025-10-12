import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import plotly.express as px
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
# Import your modules
try:
    from sheets_client import append_ticket, update_ticket_fields, get_worksheet, find_ticket_row
    from resolver import MultiModelResolver, tavily_search
    from article_suggester import (
        suggest_articles, log_ticket_resolution, get_article_analytics, 
        get_content_gaps, generate_improvement_alerts, get_article_title
    )
    from tavily_client import TAVILY_AVAILABLE, TavilySearchClient, create_search_context
    from notification_system import NotificationManager, load_config_from_env
    def get_search_client():
        return TavilySearchClient()
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all required modules are in the Python path.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Support System Dashboard", 
    layout="wide",
    page_icon="🎫"
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# Improved CSS for better text contrast
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        color: #222 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .alert-card {
        background-color: #fff3cd;
        color: #222 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
    .success-card {
        background-color: #d1edff;
        color: #222 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    /* Override Streamlit default text color for all cards and markdown */
    .stMarkdown, .stText, .stAlert, .stDataFrame, .stMetric, .stButton, .stDownloadButton, .stRadio, .stCheckbox, .stTextInput, .stTextArea, .stExpander, .stForm, .stFormSubmitButton {
        color: #222 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ticket_submitted' not in st.session_state:
    st.session_state.ticket_submitted = False
if 'current_ticket_id' not in st.session_state:
    st.session_state.current_ticket_id = None
if 'ticket_data' not in st.session_state:
    st.session_state.ticket_data = {}
if 'web_search_enabled' not in st.session_state:
    st.session_state.web_search_enabled = TAVILY_AVAILABLE

if TAVILY_AVAILABLE:
    st.sidebar.markdown("### Web Search")
    st.session_state.web_search_enabled = st.sidebar.checkbox(
        "Enable Tavily Web Search", value=st.session_state.web_search_enabled
    )

# Cached functions
@st.cache_resource(show_spinner="Loading AI resolver...")
def get_resolver():
    # Enable web search if toggled in the UI later
    return MultiModelResolver(enable_web_search=st.session_state.get('web_search_enabled', False))

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_analytics_data():
    return get_article_analytics()

@st.cache_data(ttl=300)
def load_content_gaps():
    return get_content_gaps()

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_tickets_data():
    try:
        worksheet = get_worksheet()
        records = worksheet.get_all_records()
        return records
    except Exception as e:
        st.error(f"Error loading tickets: {e}")
        return []

# Main title
st.title("🎫 AI-Powered Support System Dashboard")

# Sidebar navigation
st.sidebar.header("🧭 Navigation")
menu = st.sidebar.radio(
    "Select an option",
    [
        "📝 Submit New Ticket",
        "📊 System Analytics",
        "📈 Article Performance",
        "⚠️ Content Improvement Alerts",
        "🔔 Category Monitoring"
    ]
)

# Helper functions
def display_suggested_articles(suggestions, ticket_content):
    """Display suggested articles in an organized way"""
    if not suggestions:
        st.warning("No relevant articles found in knowledge base.")
        return
    
    st.subheader("📚 Suggested Articles")
    
    for i, doc in enumerate(suggestions, 1):
        with st.expander(f"📄 Article {i}: {get_article_title(doc)}"):
            st.write("**Source:**", doc.metadata.get('source', 'Unknown'))
            st.write("**Content Preview:**")
            st.write(doc.page_content[:400] + "..." if len(doc.page_content) > 400 else doc.page_content)
            
            # Log article view
            try:
                log_data = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "article_viewed",
                    "article": get_article_title(doc),
                    "ticket_content": ticket_content[:100]
                }
                # You could log this to a separate file for detailed analytics
            except Exception as e:
                pass

def process_ticket_submission(ticket_content, web_context=None):
    """Process a new ticket submission with all required steps, including optional web search context."""
    if not ticket_content.strip():
        st.error("Please enter a valid ticket description.")
        return None
    ticket_id = f"WEB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    timestamp = datetime.now().isoformat()
    with st.spinner("Processing your ticket..."):
        resolver = get_resolver()
        suggestions = suggest_articles(ticket_content)
        category, cat_source = resolver.safe_categorize_ticket(ticket_content)
        kb_context = "\n".join([doc.page_content[:300] for doc in suggestions])
        # If web_context is provided, append to kb_context for solution generation
        full_context = kb_context
        if web_context is not None and str(web_context).strip():
            full_context += f"\n\n[Web Search]\n{web_context}"
        solution, sol_source = resolver.safe_generate_solution(
            ticket_content,
            category,
            full_context,
            use_web_search=st.session_state.get('web_search_enabled', False),
        )
        ticket_data = {
            "ticket_id": ticket_id,
            "ticket_content": ticket_content,
            "ticket_cat": category,
            "ticket_by": "web_user",
            "ticket_status": "open",
            "ticket_timestamp": timestamp,
            "solution": solution
        }
        try:
            append_ticket(ticket_data)
            sheets_success = True
        except Exception as e:
            st.error(f"Failed to save to Google Sheets: {e}")
            sheets_success = False
        return {
            "ticket_id": ticket_id,
            "timestamp": timestamp,
            "category": category,
            "cat_source": cat_source,
            "solution": solution,
            "sol_source": sol_source,
            "suggestions": suggestions,
            "ticket_data": ticket_data,
            "sheets_success": sheets_success,
            "web_context": web_context
        }
# ===== PAGES =====

if menu == "📝 Submit New Ticket":
    st.header("📝 Submit a New Support Ticket")
    
    with st.form("ticket_form"):
        st.write("Describe your issue or question in detail:")
        ticket_content = st.text_area(
            "Ticket Description", 
            height=150,
            placeholder="Example: I'm having trouble with VS Code extensions crashing when I open large files..."
        )
        
        submit_button = st.form_submit_button("🚀 Submit Ticket", use_container_width=True)
        
        if submit_button:
            result = process_ticket_submission(ticket_content)
            
            if result:
                # Store in session state for feedback
                st.session_state.ticket_submitted = True
                st.session_state.current_ticket_id = result["ticket_id"]
                st.session_state.ticket_data = result
                
                # Display results
                st.success(f"✅ Ticket {result['ticket_id']} created successfully!")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.info(f"**Category:** {result['category']} (Source: {result['cat_source']})")
                    if result["sheets_success"]:
                        st.success("📊 Ticket saved to Google Sheets")
                    else:
                        st.warning("⚠️ Ticket not saved to Google Sheets")
                
                with col2:
                    st.info(f"**Solution Source:** {result['sol_source']}")
                    st.info(f"**Timestamp:** {result['timestamp']}")
                
                # Display suggested articles
                display_suggested_articles(result["suggestions"], ticket_content)
                
                # Display AI solution
                st.subheader("🤖 AI-Generated Solution")
                st.markdown(f"<div class='success-card'>{result['solution']}</div>", unsafe_allow_html=True)

                # Display Tavily enrichment if available
                if result.get("web_context") and "No relevant results" not in result["web_context"]:
                    st.subheader("🔎 Additional Context from Web Search")
                    st.info(result["web_context"])


    # Feedback section (shown after ticket submission)
    if st.session_state.ticket_submitted and st.session_state.current_ticket_id:
        st.divider()
        st.subheader("📋 Feedback")
        
        st.write(f"**Ticket ID:** {st.session_state.current_ticket_id}")
        st.write("Are you satisfied with the provided solution and articles?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Yes, Resolved", use_container_width=True, type="primary"):
                try:
                    # Update ticket status to resolved
                    update_ticket_fields(st.session_state.current_ticket_id, {
                        "ticket_status": "resolved"
                    })
                    
                    # Log the resolution
                    log_ticket_resolution(
                        ticket_id=st.session_state.current_ticket_id,
                        ticket_content=st.session_state.ticket_data.get("ticket_data", {}).get("ticket_content", ""),
                        category=st.session_state.ticket_data.get("category", "unknown"),
                        solution=st.session_state.ticket_data.get("solution", ""),
                        suggested_articles=st.session_state.ticket_data.get("suggestions", []),
                        user_satisfied=True
                    )
                    
                    st.success("🎉 Thank you! Your ticket has been marked as resolved.")
                    
                    # Clear session state
                    st.session_state.ticket_submitted = False
                    st.session_state.current_ticket_id = None
                    st.session_state.ticket_data = {}
                    
                except Exception as e:
                    st.error(f"Error updating ticket status: {e}")
        
        with col2:
            if st.button("❌ No, Still Need Help", use_container_width=True):
                try:
                    # Log the unsuccessful resolution
                    log_ticket_resolution(
                        ticket_id=st.session_state.current_ticket_id,
                        ticket_content=st.session_state.ticket_data.get("ticket_data", {}).get("ticket_content", ""),
                        category=st.session_state.ticket_data.get("category", "unknown"),
                        solution=st.session_state.ticket_data.get("solution", ""),
                        suggested_articles=st.session_state.ticket_data.get("suggestions", []),
                        user_satisfied=False
                    )
                    
                    st.info("📝 Your ticket remains open. Our support team will follow up with you.")
                    
                    # Optional: Allow user to provide additional info
                    additional_info = st.text_area("Additional information (optional):")
                    if st.button("Submit Additional Info") and additional_info:
                        # You could append this to the ticket or create a new entry
                        st.success("Additional information recorded.")
                    
                    # Clear session state
                    st.session_state.ticket_submitted = False
                    st.session_state.current_ticket_id = None
                    st.session_state.ticket_data = {}
                    
                except Exception as e:
                    st.error(f"Error logging feedback: {e}")

elif menu == "📋 Process Open Tickets":
    st.header("📋 Process Open Tickets")
    
    tickets = load_tickets_data()
    open_tickets = [t for t in tickets if t.get('ticket_status', '').lower() == 'open']
    
    if not open_tickets:
        st.success("🎉 No open tickets to process!")
    else:
        st.info(f"Found {len(open_tickets)} open tickets")
        
        for i, ticket in enumerate(open_tickets):
            with st.expander(f"🎫 Ticket {i+1}: {ticket.get('ticket_id', 'N/A')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Category:** {ticket.get('ticket_cat', 'N/A')}")
                    st.write(f"**Content:** {ticket.get('ticket_content', '')}")
                    st.write(f"**Created:** {ticket.get('ticket_timestamp', 'N/A')}")
                    st.write(f"**Created by:** {ticket.get('ticket_by', 'N/A')}")
                
                with col2:
                    if st.button(f"🔄 Generate Solution", key=f"solve_{ticket.get('ticket_id')}"):
                        with st.spinner("Generating solution..."):
                            resolver = get_resolver()
                            content = ticket.get('ticket_content', '')
                            category = ticket.get('ticket_cat', '')
                            
                            # Get suggestions and generate solution
                            suggestions = suggest_articles(content)
                            kb_context = "\n".join([doc.page_content[:300] for doc in suggestions])
                            solution, source = resolver.safe_generate_solution(
                                content, category, kb_context,
                                use_web_search=st.session_state.get('web_search_enabled', False)
                            )
                            
                            st.write("**Proposed Solution:**")
                            st.write(solution)
                    
                    if st.button(f"✅ Mark Resolved", key=f"resolve_{ticket.get('ticket_id')}"):
                        try:
                            update_ticket_fields(ticket.get('ticket_id'), {"ticket_status": "resolved"})
                            st.success(f"Ticket {ticket.get('ticket_id')} marked as resolved!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update ticket: {e}")

elif menu == "🗑️ Manage Resolved Tickets":
    st.header("🗑️ Manage Resolved Tickets")
    
    tickets = load_tickets_data()
    resolved_tickets = [t for t in tickets if t.get('ticket_status', '').lower() == 'resolved']
    
    if not resolved_tickets:
        st.success("No resolved tickets found!")
    else:
        st.info(f"Found {len(resolved_tickets)} resolved tickets")
        
        # Show sample of resolved tickets
        st.subheader("Recent Resolved Tickets:")
        for i, ticket in enumerate(resolved_tickets[-10:], 1):  # Show last 10
            st.write(f"{i}. **{ticket.get('ticket_id')}** - {ticket.get('ticket_cat')} - {ticket.get('ticket_timestamp', 'N/A')[:10]}")
        
        if len(resolved_tickets) > 10:
            st.write(f"... and {len(resolved_tickets) - 10} more")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete All Resolved Tickets", type="secondary"):
                st.warning("This will permanently delete all resolved tickets!")
                if st.button("⚠️ Confirm Delete All", type="primary"):
                    deleted_count = 0
                    worksheet = get_worksheet()
                    
                    with st.spinner("Deleting resolved tickets..."):
                        for ticket in resolved_tickets:
                            try:
                                row_num = find_ticket_row(ticket.get('ticket_id'))
                                if row_num:
                                    worksheet.delete_rows(row_num)
                                    deleted_count += 1
                            except Exception as e:
                                st.error(f"Failed to delete {ticket.get('ticket_id')}: {e}")
                    
                    st.success(f"Successfully deleted {deleted_count} resolved tickets!")
        
        with col2:
            # Export option
            if st.button("📥 Export Resolved Tickets"):
                df = pd.DataFrame(resolved_tickets)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"resolved_tickets_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

elif menu == "📊 System Analytics":
    st.header("📊 System Analytics Dashboard")
    
    tickets = load_tickets_data()
    
    if not tickets:
        st.info("No ticket data available yet.")
    else:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_tickets = len(tickets)
        open_tickets = len([t for t in tickets if t.get('ticket_status', '').lower() == 'open'])
        resolved_tickets = len([t for t in tickets if t.get('ticket_status', '').lower() == 'resolved'])
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
        
        with col1:
            st.metric("Total Tickets", total_tickets)
        with col2:
            st.metric("Open Tickets", open_tickets)
        with col3:
            st.metric("Resolved Tickets", resolved_tickets)
        with col4:
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution pie chart
            status_counts = {}
            for ticket in tickets:
                status = ticket.get('ticket_status', 'unknown').lower()
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig_status = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Ticket Status Distribution"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Category distribution bar chart
            category_counts = {}
            for ticket in tickets:
                category = ticket.get('ticket_cat', 'uncategorized')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            fig_category = px.bar(
                x=list(category_counts.keys()),
                y=list(category_counts.values()),
                title="Tickets by Category"
            )
            fig_category.update_layout(xaxis_title="Category", yaxis_title="Number of Tickets")
            st.plotly_chart(fig_category, use_container_width=True)
        
        # Timeline analysis
        st.subheader("📈 Ticket Timeline")
        
        # Convert timestamps and create timeline
        ticket_dates = []
        for ticket in tickets:
            timestamp = ticket.get('ticket_timestamp', '')
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                    ticket_dates.append({
                        'date': date,
                        'status': ticket.get('ticket_status', 'unknown')
                    })
                except:
                    continue
        
        if ticket_dates:
            df_timeline = pd.DataFrame(ticket_dates)
            timeline_counts = df_timeline.groupby(['date', 'status']).size().reset_index(name='count')
            
            fig_timeline = px.line(
                timeline_counts, 
                x='date', 
                y='count', 
                color='status',
                title="Ticket Creation Timeline"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

elif menu == "📈 Article Performance":
    st.header("📈 Article Performance Analytics")
    
    analytics = load_analytics_data()
    
    if analytics['total_suggestions'] == 0:
        st.info("No article usage data available yet. Submit some tickets to see analytics.")
    else:
        # Article performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Article Suggestions", analytics['total_suggestions'])
        with col2:
            st.metric("Unique Articles Used", len(analytics['most_suggested_articles']))
        with col3:
            articles_needing_improvement = len(analytics.get('articles_needing_improvement', []))
            st.metric("Articles Needing Improvement", articles_needing_improvement)
        
        # Most suggested articles
        if analytics['most_suggested_articles']:
            st.subheader("📊 Most Frequently Suggested Articles")
            
            most_suggested_df = pd.DataFrame([
                {'Article': article, 'Suggestions': count}
                for article, count in list(analytics['most_suggested_articles'].items())[:10]
            ])
            
            fig_most_suggested = px.bar(
                most_suggested_df,
                x='Suggestions',
                y='Article',
                orientation='h',
                title="Top 10 Most Suggested Articles"
            )
            fig_most_suggested.update_layout(height=400)
            st.plotly_chart(fig_most_suggested, use_container_width=True)
        
        # Article satisfaction rates
        if analytics['satisfaction_by_article']:
            st.subheader("📈 Article Satisfaction Rates")
            
            satisfaction_data = []
            for article, stats in analytics['satisfaction_by_article'].items():
                if stats['total'] >= 2:  # Only show articles used at least twice
                    satisfaction_rate = stats['satisfied'] / stats['total'] * 100
                    satisfaction_data.append({
                        'Article': article[:30] + "..." if len(article) > 30 else article,
                        'Satisfaction Rate': satisfaction_rate,
                        'Total Uses': stats['total'],
                        'Satisfied': stats['satisfied']
                    })
            
            if satisfaction_data:
                satisfaction_df = pd.DataFrame(satisfaction_data)
                satisfaction_df = satisfaction_df.sort_values('Satisfaction Rate', ascending=True)
                
                fig_satisfaction = px.bar(
                    satisfaction_df,
                    x='Satisfaction Rate',
                    y='Article',
                    orientation='h',
                    title="Article Satisfaction Rates (%)",
                    color='Satisfaction Rate',
                    color_continuous_scale='RdYlGn'
                )
                fig_satisfaction.update_layout(height=500)
                st.plotly_chart(fig_satisfaction, use_container_width=True)
                
                # Show detailed table
                st.subheader("📋 Detailed Article Performance")
                st.dataframe(satisfaction_df, use_container_width=True)
        
        # Category-Article mapping
        if analytics['category_article_mapping']:
            st.subheader("🔗 Category-Article Relationships")
            
            category_article_data = []
            for category, articles in analytics['category_article_mapping'].items():
                for article, count in articles.items():
                    category_article_data.append({
                        'Category': category,
                        'Article': article[:25] + "..." if len(article) > 25 else article,
                        'Usage Count': count
                    })
            
            if category_article_data:
                category_df = pd.DataFrame(category_article_data)
                
                # Create heatmap-style visualization
                pivot_data = category_df.pivot_table(
                    index='Category', 
                    columns='Article', 
                    values='Usage Count', 
                    fill_value=0
                )
                
                fig_heatmap = px.imshow(
                    pivot_data.values,
                    labels=dict(x="Article", y="Category", color="Usage Count"),
                    y=pivot_data.index,
                    x=pivot_data.columns,
                    title="Category-Article Usage Heatmap"
                )
                fig_heatmap.update_layout(height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)

elif menu == "⚠️ Content Improvement Alerts":
    st.header("⚠️ Content Improvement Alerts")
    
    alerts = generate_improvement_alerts()
    gaps = load_content_gaps()
    
    if not alerts and not gaps.get('low_coverage_topics'):
        st.success("🎉 No improvement alerts at this time! Your content appears to be performing well.")
    else:
        # Priority alerts
        if alerts:
            st.subheader("🚨 Priority Improvement Alerts")
            
            high_priority = [a for a in alerts if a.get('priority') == 'high']
            medium_priority = [a for a in alerts if a.get('priority') == 'medium']
            
            if high_priority:
                st.error("**High Priority Issues:**")
                for alert in high_priority:
                    st.markdown(f"""
                    <div class='alert-card'>
                        <strong>{alert.get('type', 'Unknown').replace('_', ' ').title()}:</strong><br>
                        {alert.get('message', 'No message')}<br>
                        <strong>Action:</strong> {alert.get('action', 'No action specified')}
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
            
            if medium_priority:
                st.warning("**Medium Priority Issues:**")
                for alert in medium_priority:
                    st.markdown(f"""
                    <div class='alert-card'>
                        <strong>{alert.get('type', 'Unknown').replace('_', ' ').title()}:</strong><br>
                        {alert.get('message', 'No message')}<br>
                        <strong>Action:</strong> {alert.get('action', 'No action specified')}
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
        
        # Content gaps analysis
        if gaps.get('low_coverage_topics'):
            st.subheader("📊 Content Gap Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Topics with High Unsatisfied Tickets:**")
                for topic in gaps['low_coverage_topics']:
                    st.write(f"- **{topic['category']}**: {topic['unsatisfied_count']} unsatisfied tickets")
            
            with col2:
                st.write("**Frequently Mentioned Keywords in Unsatisfied Tickets:**")
                for keyword in gaps.get('frequent_unsatisfied_queries', [])[:5]:
                    st.write(f"- **{keyword['keyword']}**: mentioned {keyword['frequency']} times")
        
        # Suggested new articles
        if gaps.get('suggested_new_articles'):
            st.subheader("💡 Suggested New Articles")
            
            for suggestion in gaps['suggested_new_articles']:
                priority_color = "🔴" if suggestion['priority'] == 'high' else "🟡"
                st.write(f"{priority_color} **{suggestion['topic']}** ({suggestion['priority']} priority)")
                st.write(f"   {suggestion['description']}")
        
        # Action buttons
        st.divider()
        st.subheader("🛠️ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Analytics", use_container_width=True):
                st.cache_data.clear()
                st.success("Analytics refreshed!")
                st.rerun()
        
        with col2:
            if st.button("📥 Export Report", use_container_width=True):
                report_data = {
                    "timestamp": datetime.now().isoformat(),
                    "alerts": alerts,
                    "content_gaps": gaps,
                    "analytics": load_analytics_data()
                }
                
                report_json = json.dumps(report_data, indent=2)
                st.download_button(
                    label="Download JSON Report",
                    data=report_json,
                    file_name=f"improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
                st.warning("This will permanently delete all analytics data!")
                if st.checkbox("I understand this action cannot be undone"):
                    if st.button("⚠️ Confirm Clear Data"):
                        from article_suggester import clear_analytics_data
                        if clear_analytics_data():
                            st.success("Analytics data cleared!")
                            st.rerun()
                        else:
                            st.error("Failed to clear analytics data")

elif menu == "🔔 Category Monitoring":
    st.header("🔔 Category Performance Monitoring")
    
    # Configuration section
    st.subheader("⚙️ Notification Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Slack Settings**")
        slack_enabled = st.checkbox("Enable Slack Notifications", value=False)
        slack_webhook = st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/services/...")
        slack_channel = st.text_input("Slack Channel", value="#support-alerts")
    
    with col2:
        st.markdown("**Email Settings**")
        email_enabled = st.checkbox("Enable Email Notifications", value=False)
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587)
        admin_email = st.text_input("Admin Email", placeholder="admin@yourcompany.com")
    
    # Monitoring thresholds
    st.subheader("📊 Monitoring Thresholds")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        satisfaction_threshold = st.slider("Satisfaction Threshold", 0.0, 1.0, 0.6, 0.1)
        min_tickets = st.number_input("Min Tickets for Analysis", value=5)
    
    with col2:
        volume_threshold = st.number_input("Volume Alert Threshold", value=10)
        time_window = st.number_input("Time Window (hours)", value=24)
    
    with col3:
        cooldown_hours = st.number_input("Notification Cooldown (hours)", value=6)
    
    # Manual monitoring check
    st.subheader("🔍 Manual Monitoring Check")
    
    if st.button("🚀 Run Category Analysis", use_container_width=True):
        with st.spinner("Analyzing category performance..."):
            try:
                # Create temporary config
                from notification_system import NotificationConfig
                config = NotificationConfig(
                    slack_enabled=slack_enabled,
                    slack_webhook_url=slack_webhook,
                    slack_channel=slack_channel,
                    smtp_enabled=email_enabled,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_username="",  # Would need to be configured
                    smtp_password="",  # Would need to be configured
                    admin_email=admin_email,
                    min_tickets_for_analysis=min_tickets,
                    satisfaction_threshold=satisfaction_threshold,
                    volume_threshold=volume_threshold,
                    time_window_hours=time_window,
                    cooldown_hours=cooldown_hours
                )
                
                manager = NotificationManager(config)
                
                # Run analysis
                category_stats = manager.monitor.analyze_category_performance()
                problematic_categories = manager.monitor.identify_problematic_categories(category_stats)
                
                # Display results
                if not category_stats:
                    st.warning("No ticket data found for analysis")
                else:
                    st.success(f"Analysis complete! Found {len(category_stats)} categories with data")
                    
                    # Show category performance
                    st.subheader("📈 Category Performance Summary")
                    
                    if category_stats:
                        # Create performance dataframe
                        perf_data = []
                        for category, stats in category_stats.items():
                            perf_data.append({
                                'Category': category,
                                'Total Tickets': stats['total_tickets'],
                                'Satisfied': stats['satisfied_tickets'],
                                'Unsatisfied': stats['unsatisfied_tickets'],
                                'Satisfaction Rate': f"{stats['satisfaction_rate']:.1%}",
                                'Status': '✅ Good' if stats['satisfaction_rate'] >= satisfaction_threshold else '⚠️ Needs Attention'
                            })
                        
                        perf_df = pd.DataFrame(perf_data)
                        st.dataframe(perf_df, use_container_width=True)
                        
                        # Show problematic categories
                        if problematic_categories:
                            st.subheader("🚨 Problematic Categories")
                            
                            for cat_report in problematic_categories:
                                category = cat_report['category']
                                stats = cat_report['stats']
                                issues = cat_report['issues']
                                priority = cat_report['priority']
                                
                                priority_color = "🔴" if priority == 'high' else "🟡"
                                
                                with st.expander(f"{priority_color} {category.upper()} ({priority.upper()} PRIORITY)"):
                                    st.write(f"**Satisfaction Rate:** {stats['satisfaction_rate']:.1%} ({stats['satisfied_tickets']}/{stats['total_tickets']})")
                                    st.write(f"**Volume:** {stats['total_tickets']} tickets in {time_window} hours")
                                    
                                    st.write("**Issues Identified:**")
                                    for issue in issues:
                                        severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡"
                                        st.write(f"- {severity_emoji} {issue['message']}")
                                    
                                    # Show recent tickets
                                    if stats['recent_tickets']:
                                        st.write("**Recent Tickets:**")
                                        for ticket in stats['recent_tickets'][-5:]:
                                            status_emoji = "✅" if ticket['satisfied'] else "❌"
                                            st.write(f"- {status_emoji} {ticket['content']}...")
                        else:
                            st.success("🎉 All categories are performing well!")
                    
                    # Test notifications
                    if problematic_categories and (slack_enabled or email_enabled):
                        st.subheader("📤 Test Notifications")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if slack_enabled and slack_webhook:
                                if st.button("📱 Send Slack Test"):
                                    try:
                                        from notification_system import SlackNotifier
                                        notifier = SlackNotifier(slack_webhook, slack_channel)
                                        success = notifier.send_alert(problematic_categories)
                                        if success:
                                            st.success("Slack notification sent!")
                                        else:
                                            st.error("Failed to send Slack notification")
                                    except Exception as e:
                                        st.error(f"Slack error: {e}")
                        
                        with col2:
                            if email_enabled and admin_email:
                                st.info("Email notifications require SMTP credentials to be configured in environment variables")
                
            except Exception as e:
                st.error(f"Error running analysis: {e}")
    
    # Scheduled monitoring info
    st.subheader("⏰ Automated Monitoring")
    
    st.info("""
    **Automated Monitoring Setup:**
    
    To enable automatic monitoring, you can:
    
    1. **Run the scheduler script:**
       ```bash
       python src/notification_scheduler.py
       ```
    
    2. **Set up environment variables** in a `.env` file:
       ```
       SLACK_ENABLED=true
       SLACK_WEBHOOK_URL=your_webhook_url
       ADMIN_EMAIL=admin@yourcompany.com
       # ... other settings
       ```
    
    3. **Configure thresholds** as needed for your organization.
    
    The system will automatically check category performance every 2 hours and send alerts when thresholds are exceeded.
    """)

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🤖 AI-Powered Support System Dashboard<br>
        Powered by Streamlit & LangChain
    </div>
    """, unsafe_allow_html=True)