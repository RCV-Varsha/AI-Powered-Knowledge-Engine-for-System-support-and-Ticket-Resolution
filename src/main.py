"""
Complete AI-powered ticket management system with RAG, knowledge base integration, and Tavily web search.
"""

import sys
from datetime import datetime
import uuid
from article_suggester import suggest_articles

from sheets_client import (
    append_ticket, 
    update_ticket_fields, 
    get_worksheet, 
    find_ticket_row
)
from kb_processor import load_kb_retriever, MarkdownProcessor
from resolver import MultiModelResolver

# Import Tavily integration
try:
    from tavily_client import TavilySearchClient, create_search_context
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

class TicketSystem:
    def __init__(self, enable_web_search=True):
        self.resolver = None
        self.kb_retriever = None
        self.web_search_enabled = enable_web_search and TAVILY_AVAILABLE
        self._initialize_kb_and_resolver()

    def _initialize_kb_and_resolver(self):
        print("🚀 Initializing Knowledge Base and AI Systems...")
        
        # Initialize KB
        processor = MarkdownProcessor()
        if not processor.process_and_index_kb(rebuild=False):
            print("⚠️ Knowledge base initialization failed. Solutions may be limited.")
        else:
            self.kb_retriever = load_kb_retriever()
            print("✅ Knowledge base ready.")
        
        # Initialize resolver with web search
        self.resolver = MultiModelResolver(enable_web_search=self.web_search_enabled)
        print("✅ Multi-model resolver ready.")
        
        # Show web search status
        if self.resolver:
            search_status = self.resolver.get_search_status()
            if search_status["web_search_enabled"]:
                print("🌐 Web search integration: ENABLED")
            else:
                print("⚠️ Web search integration: DISABLED")
                if not TAVILY_AVAILABLE:
                    print("   Reason: Tavily package not installed (pip install tavily-python)")
                elif not search_status["search_client_available"]:
                    print("   Reason: Tavily API key not found (set TAVILY_API_KEY environment variable)")

    def _get_kb_context(self, user_query, max_chunks=2):
        """Retrieve KB context for a given query using retriever, formatted for prompt."""
        kb_context = ""
        if self.kb_retriever:
            try:
                docs = self.kb_retriever.get_relevant_documents(user_query)
                for i, doc in enumerate(docs[:max_chunks], 1):
                    content = doc.page_content[:350].replace('\n', ' ')
                    source = doc.metadata.get('source', 'Documentation')
                    kb_context += f"\n{i}. From {source}: {content}..."
            except Exception as e:
                print(f"⚠️ Error retrieving KB context: {e}")
        return kb_context

    def display_menu(self):
        print("\n" + "="*70)
        print("🎫 AI-POWERED SMART SUPPORT & TICKETING SYSTEM")
        web_status = "🌐 WEB SEARCH ENABLED" if self.web_search_enabled else "📚 KB ONLY MODE"
        print(f"   {web_status}")
        print("="*70)
        print("1. 📋 Show Open Tickets")
        print("2. ⚙️  Process Open Tickets")
        print("3. 🤖 Interactive Mode (Create New Ticket)")
        print("4. 🗑️  Delete Resolved Tickets")
        print("5. 📊 Show System Statistics")
        print("6. 🔧 System Settings & Status")
        print("7. 🌐 Test Web Search (if enabled)")
        print("8. 🚪 Exit")
        print("="*70)

    def show_open_tickets(self):
        print("\n📋 OPEN TICKETS")
        print("-"*50)
        try:
            worksheet = get_worksheet()
            records = worksheet.get_all_records()
            open_tickets = [r for r in records if r.get('ticket_status', '').lower() == 'open']
            if not open_tickets:
                print("✅ No open tickets found!")
                return
            for i, ticket in enumerate(open_tickets, 1):
                print(f"\n{i}. Ticket ID: {ticket.get('ticket_id', 'N/A')}")
                print(f"   Category: {ticket.get('ticket_cat', 'N/A')}")
                print(f"   Content: {ticket.get('ticket_content', 'N/A')[:100]}...")
                print(f"   Created: {ticket.get('ticket_timestamp', 'N/A')}")
            print(f"\n📊 Total open tickets: {len(open_tickets)}")
        except Exception as e:
            print(f"❌ Error retrieving tickets: {e}")

    def process_open_tickets(self):
        print("\n⚙️ PROCESSING OPEN TICKETS")
        print("-"*50)
        try:
            worksheet = get_worksheet()
            records = worksheet.get_all_records()
            open_tickets = [r for r in records if r.get('ticket_status', '').lower() == 'open']
            if not open_tickets:
                print("✅ No open tickets to process!")
                return
                
            # Ask about web search preference
            use_web_search = True
            if self.web_search_enabled:
                web_choice = input("\n🌐 Use web search for enhanced solutions? (y/n, default=y): ").lower().strip()
                use_web_search = web_choice != 'n'
                
            for i, ticket in enumerate(open_tickets, 1):
                ticket_id = ticket.get('ticket_id')
                content = ticket.get('ticket_content', '')
                category = ticket.get('ticket_cat', '')
                print(f"\n🎫 Processing Ticket {i}/{len(open_tickets)}: {ticket_id}")
                print(f"📂 Category: {category}")
                print(f"📝 Content: {content[:100]}...")

                # Get KB context
                kb_context = self._get_kb_context(content)

                if self.resolver:
                    print("🤖 Generating AI solution...")
                    if use_web_search and self.web_search_enabled:
                        print("🌐 Including web search results...")
                    
                    solution, sol_source = self.resolver.safe_generate_solution(
                        content, category, kb_context, use_web_search
                    )
                    print(f"💡 Proposed Solution ({sol_source}):")
                    print("-" * 40)
                    print(solution[:500] + "..." if len(solution) > 500 else solution)
                    print("-" * 40)
                    
                    choice = input("\n✅ Mark this ticket as resolved? (y/n/s=skip): ").lower().strip()
                    if choice == 'y':
                        try:
                            update_ticket_fields(ticket_id, {
                                "ticket_status": "resolved",
                                "ticket_timestamp": datetime.now().isoformat()
                            })
                            print(f"✅ Ticket {ticket_id} marked as resolved")
                        except Exception as e:
                            print(f"❌ Failed to update ticket: {e}")
                    elif choice == 's':
                        continue
                else:
                    print("⚠️ Resolver not available")
                    
                if i < len(open_tickets):
                    proceed = input("\n➡️ Continue to next ticket? (y/n): ").lower().strip()
                    if proceed != 'y':
                        break
        except Exception as e:
            print(f"❌ Error processing tickets: {e}")

    def interactive_mode(self):
        print("\n🤖 INTERACTIVE MODE")
        print("-"*50)
        print("Welcome! I'll help you with your VS Code extension support query.")
        
        # Ask about web search preference
        use_web_search = True
        if self.web_search_enabled:
            web_choice = input("🌐 Enable web search for enhanced solutions? (y/n, default=y): ").lower().strip()
            use_web_search = web_choice != 'n'
            
        while True:
            print("\n" + "="*50)
            user_query = input("🎫 Enter your question or issue (or 'exit' to return): ").strip()
            if user_query.lower() in ['exit', 'quit', 'back']:
                break
            if not user_query:
                print("⚠️ Please enter a valid question.")
                continue
            
            ticket_id = f"INT-{uuid.uuid4().hex[:8].upper()}"
            print(f"\n🔄 Processing your ticket: {ticket_id}")
            print("🤖 Analyzing your query...")
            
            # Get article suggestions
            suggestions = suggest_articles(user_query)
            if suggestions:
                print("\n🔎 Suggested Articles:")
                for i, doc in enumerate(suggestions, 1):
                    print(f"{i}. {doc.metadata.get('source', 'Unknown')}: {doc.page_content[:200]}...")
            else:
                print("\n🔎 No relevant articles found.")
            
            # Categorize ticket
            category, cat_source = self.resolver.safe_categorize_ticket(user_query)
            print(f"📂 Category: {category} (Source: {cat_source})")

            # Get KB context
            kb_context = self._get_kb_context(user_query)

            if self.resolver:
                print("💭 Generating comprehensive solution...")
                if use_web_search and self.web_search_enabled:
                    print("🌐 Searching web for latest information...")
                    
                solution, sol_source = self.resolver.safe_generate_solution(
                    user_query, category, kb_context, use_web_search
                )
                
                print(f"\n💡 COMPREHENSIVE SOLUTION ({sol_source}):")
                print("=" * 60)
                print(solution)
                print("=" * 60)
                
                satisfaction = input("\n❓ Are you satisfied with this solution? (y/n): ").lower().strip()
                if satisfaction == 'y':
                    ticket_status = "resolved"
                    print("🎉 Great! Marking ticket as resolved.")
                else:
                    ticket_status = "open"
                    print("📝 Ticket will remain open for further assistance.")
                    additional_info = input("📋 Any additional information to help us better? (optional): ").strip()
                    if additional_info:
                        user_query += f" Additional info: {additional_info}"
            else:
                print("⚠️ Resolver not available. Ticket will be created for manual review.")
                ticket_status = "open"
                solution = "AI resolver unavailable - manual review required"
                
            print("💾 Saving ticket to system...")
            ticket_data = {
                "ticket_id": ticket_id,
                "ticket_content": user_query,
                "ticket_cat": category,
                "ticket_by": "interactive_user",
                "ticket_status": ticket_status,
                "ticket_timestamp": datetime.now().isoformat()
            }
            
            try:
                append_ticket(ticket_data)
                print(f"✅ Ticket {ticket_id} saved successfully!")
            except Exception as e:
                print(f"❌ Failed to save ticket: {e}")
                
            print(f"\n📊 Session Summary:")
            print(f"   Ticket ID: {ticket_id}")
            print(f"   Category: {category}")
            print(f"   Status: {ticket_status}")
            print(f"   Web Search: {'Used' if use_web_search and self.web_search_enabled else 'Not used'}")
            
            continue_session = input("\n❓ Do you have another question? (y/n): ").lower().strip()
            if continue_session != 'y':
                print("👋 Thank you for using our support system!")
                break

    def delete_resolved_tickets(self):
        print("\n🗑️ DELETE RESOLVED TICKETS")
        print("-"*50)
        try:
            worksheet = get_worksheet()
            records = worksheet.get_all_records()
            resolved_tickets = [r for r in records if r.get('ticket_status', '').lower() == 'resolved']
            if not resolved_tickets:
                print("✅ No resolved tickets found!")
                return
            print(f"📋 Found {len(resolved_tickets)} resolved tickets:")
            for i, ticket in enumerate(resolved_tickets[:5], 1):
                print(f"{i}. {ticket.get('ticket_id')} - {ticket.get('ticket_cat')}")
            if len(resolved_tickets) > 5:
                print(f"... and {len(resolved_tickets) - 5} more")
            confirm = input(f"\n⚠️ Delete all {len(resolved_tickets)} resolved tickets? (y/n): ").lower().strip()
            if confirm == 'y':
                deleted_count = 0
                for ticket in resolved_tickets:
                    ticket_id = ticket.get('ticket_id')
                    row_num = find_ticket_row(ticket_id)
                    if row_num:
                        try:
                            worksheet.delete_rows(row_num)
                            deleted_count += 1
                            print(f"🗑️ Deleted: {ticket_id}")
                        except Exception as e:
                            print(f"❌ Failed to delete {ticket_id}: {e}")
                print(f"✅ Successfully deleted {deleted_count} resolved tickets!")
            else:
                print("❌ Deletion cancelled.")
        except Exception as e:
            print(f"❌ Error during deletion: {e}")

    def show_statistics(self):
        print("\n📊 SYSTEM STATISTICS")
        print("-"*50)
        try:
            worksheet = get_worksheet()
            records = worksheet.get_all_records()
            if not records:
                print("📋 No tickets found in the system.")
                return
                
            status_counts = {}
            category_counts = {}
            for record in records:
                status = record.get('ticket_status', 'unknown').lower()
                category = record.get('ticket_cat', 'uncategorized')
                status_counts[status] = status_counts.get(status, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1
                
            print(f"📈 Total Tickets: {len(records)}")
            print(f"\n🎯 By Status:")
            for status, count in sorted(status_counts.items()):
                print(f"   • {status.title()}: {count}")
            print(f"\n📂 By Category:")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {category}: {count}")
                
            recent = records[-5:] if len(records) >= 5 else records
            print(f"\n🕒 Recent Tickets:")
            for ticket in recent:
                print(f"   • {ticket.get('ticket_id')} - {ticket.get('ticket_cat')} ({ticket.get('ticket_status')})")
        except Exception as e:
            print(f"❌ Error retrieving statistics: {e}")

    def show_system_status(self):
        print("\n🔧 SYSTEM STATUS & SETTINGS")
        print("-" * 50)
        
        # Test connections
        print("🔗 Testing Connections:")
        try:
            worksheet = get_worksheet()
            print("   ✅ Google Sheets: Connected")
        except Exception as e:
            print(f"   ❌ Google Sheets: Error - {e}")
        
        if self.kb_retriever:
            print("   ✅ Knowledge Base: Loaded")
        else:
            print("   ⚠️ Knowledge Base: Limited functionality")
            
        if self.resolver:
            search_status = self.resolver.get_search_status()
            print("\n🤖 AI Resolver Status:")
            print(f"   • HuggingFace Models: {'Available' if self.resolver.llm else 'Not available'}")
            print(f"   • Embeddings: {'Available' if self.resolver.embeddings else 'Not available'}")
            print(f"   • Pattern Matching: Available")
            
            print("\n🌐 Web Search Integration:")
            print(f"   • Tavily Package: {'Installed' if TAVILY_AVAILABLE else 'Not installed'}")
            print(f"   • Web Search: {'Enabled' if search_status['web_search_enabled'] else 'Disabled'}")
            print(f"   • Search Client: {'Ready' if search_status['search_client_available'] else 'Not available'}")
            
            if not search_status['web_search_enabled']:
                print("\n💡 To enable web search:")
                if not TAVILY_AVAILABLE:
                    print("   1. Install Tavily: pip install tavily-python")
                print("   2. Get API key from: https://app.tavily.com")
                print("   3. Set environment variable: TAVILY_API_KEY=your_key")
        else:
            print("   ❌ AI Resolver: Not initialized")
        
        print(f"\n📊 System Statistics:")
        try:
            worksheet = get_worksheet()
            records = worksheet.get_all_records()
            open_count = len([r for r in records if r.get('ticket_status', '').lower() == 'open'])
            resolved_count = len([r for r in records if r.get('ticket_status', '').lower() == 'resolved'])
            print(f"   • Total Tickets: {len(records)}")
            print(f"   • Open Tickets: {open_count}")
            print(f"   • Resolved Tickets: {resolved_count}")
            print(f"   • Resolution Rate: {(resolved_count/len(records)*100):.1f}%" if records else "N/A")
        except Exception as e:
            print(f"   ❌ Could not load statistics: {e}")

    def test_web_search(self):
        print("\n🌐 WEB SEARCH TEST")
        print("-" * 50)
        
        if not self.web_search_enabled:
            print("❌ Web search is not enabled.")
            print("Please check your Tavily setup and API key.")
            return
            
        if not self.resolver or not self.resolver.search_client:
            print("❌ Search client not available.")
            return
            
        test_queries = [
            ("VS Code extension crashes on startup", "bug_report"),
            ("How to debug VS Code extension", "troubleshooting"),
            ("VS Code extension API documentation", "documentation")
        ]
        
        print("Testing web search with sample queries:")
        for query, category in test_queries:
            print(f"\n🔍 Query: {query}")
            print(f"📂 Category: {category}")
            print("-" * 30)
            
            try:
                search_results = self.resolver.search_web_for_solution(query, category)
                if search_results and search_results.get("success"):
                    results = search_results.get("results", [])
                    print(f"✅ Found {len(results)} results")
                    if search_results.get("answer"):
                        print(f"🤖 AI Summary: {search_results['answer'][:150]}...")
                    
                    for i, result in enumerate(results[:2], 1):  # Show first 2 results
                        print(f"  {i}. {result['title']}")
                        print(f"     {result['url']}")
                        print(f"     Score: {result['score']:.2f}")
                else:
                    print("❌ Search failed or returned no results")
                    if search_results:
                        print(f"Error: {search_results.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Search error: {e}")
            
            print()

    def run(self):
        print("🚀 Starting AI-Powered Smart Support & Ticketing System...")
        print("🔧 Testing system connections...")
        
        try:
            worksheet = get_worksheet()
            print("✅ Google Sheets connection: OK")
        except Exception as e:
            print(f"❌ Google Sheets connection error: {e}")
            print("Some features may not work properly.")
            
        if self.kb_retriever:
            print("✅ Knowledge Base: OK")
        else:
            print("⚠️ Knowledge Base: Limited functionality")
            
        if self.web_search_enabled:
            print("✅ Web Search: ENABLED")
        else:
            print("⚠️ Web Search: DISABLED")
            
        while True:
            try:
                self.display_menu()
                choice = input(f"\n🎯 Select an option (1-8): ").strip()
                
                if choice == '1':
                    self.show_open_tickets()
                elif choice == '2':
                    self.process_open_tickets()
                elif choice == '3':
                    self.interactive_mode()
                elif choice == '4':
                    self.delete_resolved_tickets()
                elif choice == '5':
                    self.show_statistics()
                elif choice == '6':
                    self.show_system_status()
                elif choice == '7':
                    self.test_web_search()
                elif choice == '8':
                    print("\n👋 Thank you for using the AI Support System!")
                    print("🎉 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-8.")
                    
                if choice in ['1', '5', '6', '7']:
                    input("\n📌 Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️ System interrupted by user.")
                print("👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("🔄 Returning to main menu...")

def main():
    try:
        # Check if user wants to disable web search
        enable_search = True
        if len(sys.argv) > 1 and sys.argv[1] == "--no-web-search":
            enable_search = False
            print("🌐 Web search disabled by command line flag")
        
        system = TicketSystem(enable_web_search=enable_search)
        system.run()
    except Exception as e:
        print(f"❌ Critical system error: {e}")
        print("🔧 Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()