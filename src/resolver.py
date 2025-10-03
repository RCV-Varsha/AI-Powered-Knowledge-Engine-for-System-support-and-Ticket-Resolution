import os
import sys
import json
from pathlib import Path
import logging
import difflib
import re

# Import Tavily client
try:
    from tavily_client import TavilySearchClient, create_search_context
    TAVILY_INTEGRATION = True
except ImportError:
    TAVILY_INTEGRATION = False
    logging.warning("Tavily integration not available. Web search features disabled.")

logging.basicConfig(level=logging.INFO)

def get_allowed_categories():
    """Extract unique expected categories from pilot dataset"""
    dataset_path = Path("data/pilot_dataset_augmented.json")
    categories = set()
    
    if dataset_path.exists():
        try:
            with open(dataset_path, encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if "expected_category" in item:
                        categories.add(item["expected_category"].strip().lower().replace(" ", "_"))
        except Exception as e:
            logging.warning(f"Could not load augmented dataset: {e}")
    
    # If we got categories from the file, use those
    if categories:
        return sorted(categories)
    
    # Default categories that match your pilot dataset
    default_categories = [
        "bug_report",
        "feature_request", 
        "technical_issue",
        "documentation",
        "performance",
        "authentication", 
        "integration",
        "ui_ux",
        "installation",
        "configuration",
        "troubleshooting",
        "general_query"
    ]
    
    logging.info(f"Using default categories: {default_categories}")
    return default_categories


class MultiModelResolver:
    def __init__(self, model_name="microsoft/DialoGPT-medium", enable_web_search=True):
        logging.info("Initializing MultiModelResolver with HuggingFace and Tavily...")

        # Track provider
        self.llm_provider = "huggingface"
        self.quota_exceeded = False

        # Load categories
        self.category_list = get_allowed_categories()
        logging.info(f"Loaded {len(self.category_list)} categories: {self.category_list}")

        # Try to initialize HuggingFace model
        self.llm = self._initialize_hf_model(model_name)

        # Initialize embeddings for similarity matching
        self.embeddings = self._initialize_embeddings()

        # Initialize the pattern-based categorizer
        self.pattern_categorizer = self._init_pattern_categorizer()

        # Initialize Tavily search client
        self.web_search_enabled = enable_web_search and TAVILY_INTEGRATION
        self.search_client = None
        
        if self.web_search_enabled:
            try:
                self.search_client = TavilySearchClient()
                if self.search_client.is_available():
                    logging.info("Tavily web search integration enabled")
                else:
                    self.web_search_enabled = False
                    logging.warning("Tavily search not available - missing API key or setup issues")
            except Exception as e:
                logging.error(f"Failed to initialize Tavily search: {e}")
                self.web_search_enabled = False

    def _initialize_hf_model(self, model_name):
        """Initialize HuggingFace model"""
        try:
            from transformers import pipeline
            
            # For classification, use a text-classification pipeline
            # You can also use text-generation models
            classifier = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",  # Good for zero-shot classification
                device=-1  # Use CPU, set to 0 for GPU
            )
            
            logging.info(f"Successfully initialized HuggingFace model: facebook/bart-large-mnli")
            return classifier
            
        except ImportError as e:
            logging.error(f"Could not import transformers: {e}")
            logging.info("Please install: pip install transformers torch")
            return None
        except Exception as e:
            logging.error(f"Failed to initialize HuggingFace model: {e}")
            return None

    def _initialize_embeddings(self):
        """Initialize embeddings for similarity matching"""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            logging.info("Initialized sentence transformers embeddings")
            return model
        except ImportError:
            logging.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
            return None
        except Exception as e:
            logging.warning(f"Could not initialize embeddings: {e}")
            return None

    def _init_pattern_categorizer(self):
        """Initialize pattern-based categorizer"""
        patterns = {
            "bug_report": {
                "keywords": ["bug", "error", "crash", "broken", "not working", "issue", "problem", 
                            "exception", "fail", "doesn't work", "stopped working", "malfunction"],
                "patterns": [r"error.*code", r"crash.*when", r"doesn't.*work", r"not.*working",
                           r"throws.*error", r"getting.*error"]
            },
            "feature_request": {
                "keywords": ["feature", "request", "suggestion", "enhance", "improvement", "add", 
                            "new", "would like", "wish", "could you", "please add", "enhancement"],
                "patterns": [r"would.*like", r"could.*you.*add", r"please.*add", r"feature.*request",
                           r"suggestion.*for", r"enhance.*with"]
            },
            "technical_issue": {
                "keywords": ["install", "installation", "setup", "configure", "configuration", 
                            "permission", "access", "compatibility", "version", "update", "upgrade"],
                "patterns": [r"how.*to.*install", r"setup.*issue", r"configuration.*problem",
                           r"compatibility.*with", r"version.*conflict"]
            },
            "documentation": {
                "keywords": ["documentation", "docs", "guide", "tutorial", "help", "how to", 
                            "example", "usage", "manual", "instructions", "readme"],
                "patterns": [r"how.*to.*use", r"where.*is.*documentation", r"need.*help.*with",
                           r"tutorial.*for", r"guide.*on"]
            },
            "performance": {
                "keywords": ["slow", "performance", "speed", "lag", "memory", "cpu", "optimization",
                            "freeze", "hang", "timeout", "delay", "takes forever"],
                "patterns": [r"runs.*slow", r"performance.*issue", r"takes.*long.*time",
                           r"memory.*usage", r"cpu.*high"]
            },
            "integration": {
                "keywords": ["integration", "api", "webhook", "connect", "sync", "import", "export",
                            "third party", "external", "plugin", "extension compatibility"],
                "patterns": [r"integrate.*with", r"connect.*to", r"api.*not.*working",
                           r"sync.*with", r"import.*from"]
            },
            "ui_ux": {
                "keywords": ["interface", "ui", "ux", "design", "layout", "theme", "color", "font",
                            "button", "menu", "display", "visual", "appearance"],
                "patterns": [r"ui.*issue", r"interface.*problem", r"design.*bug",
                           r"layout.*broken", r"display.*incorrect"]
            },
            "authentication": {
                "keywords": ["login", "authentication", "auth", "password", "credentials", "token",
                            "oauth", "signin", "sign in", "account", "access denied"],
                "patterns": [r"login.*fail", r"authentication.*error", r"access.*denied",
                           r"credentials.*invalid", r"token.*expired"]
            },
            "installation": {
                "keywords": ["install", "installation", "setup", "download", "package", "npm", "pip"],
                "patterns": [r"install.*error", r"setup.*fail", r"download.*problem"]
            },
            "configuration": {
                "keywords": ["config", "configuration", "settings", "setup", "preferences"],
                "patterns": [r"config.*error", r"settings.*not.*working"]
            },
            "troubleshooting": {
                "keywords": ["troubleshoot", "debug", "fix", "solve", "resolve"],
                "patterns": [r"how.*to.*fix", r"troubleshoot.*issue"]
            }
        }
        return patterns

    def categorize_ticket(self, ticket_content):
        """Categorize ticket using available methods"""
        
        # 1. Try HuggingFace model first if available
        if self.llm and not self.quota_exceeded:
            try:
                category = self._categorize_with_hf(ticket_content)
                if category:
                    return category, self.llm_provider
            except Exception as e:
                logging.warning(f"HuggingFace categorization failed: {e}")
                
        # 2. Try embeddings similarity if available
        if self.embeddings:
            try:
                category = self._categorize_with_embeddings(ticket_content)
                if category:
                    return category, "embeddings"
            except Exception as e:
                logging.warning(f"Embeddings categorization failed: {e}")
                
        # 3. Fall back to pattern matching
        category = self._categorize_with_patterns(ticket_content)
        if category:
            return category, "patterns"
            
        # 4. Default fallback
        return "general_query", "default"

    def _categorize_with_hf(self, ticket_content):
        """Categorize using HuggingFace zero-shot classification"""
        try:
            # Format categories for natural language
            candidate_labels = [cat.replace("_", " ") for cat in self.category_list]
            
            result = self.llm(ticket_content, candidate_labels)
            
            if result and 'labels' in result and 'scores' in result:
                best_label = result['labels'][0]
                confidence = result['scores'][0]
                
                if confidence > 0.3:  # Minimum confidence threshold
                    # Convert back to underscore format
                    predicted_category = best_label.replace(" ", "_")
                    
                    # Find closest match in our category list
                    matches = difflib.get_close_matches(predicted_category, self.category_list, n=1, cutoff=0.7)
                    if matches:
                        return matches[0]
                    
                    # Direct match check
                    if predicted_category in self.category_list:
                        return predicted_category
                        
            return None
            
        except Exception as e:
            logging.error(f"HuggingFace classification failed: {e}")
            return None

    def _categorize_with_embeddings(self, ticket_content):
        """Categorize using embeddings similarity"""
        try:
            # Create example texts for each category
            category_examples = {
                "bug_report": "The application crashes with an error when I try to use this feature",
                "feature_request": "Please add a new feature to improve functionality",
                "technical_issue": "I'm having trouble installing and configuring the software",
                "documentation": "Where can I find help and tutorials for using this",
                "performance": "The application is running very slowly and using too much memory",
                "authentication": "I cannot log in with my credentials",
                "integration": "How do I connect this with external APIs and services",
                "ui_ux": "The user interface layout is broken and buttons don't work"
            }
            
            # Get embeddings for ticket content
            ticket_embedding = self.embeddings.encode([ticket_content])
            
            # Get embeddings for category examples
            category_embeddings = self.embeddings.encode(list(category_examples.values()))
            
            # Calculate similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(ticket_embedding, category_embeddings)[0]
            
            # Find best match
            best_idx = similarities.argmax()
            best_score = similarities[best_idx]
            
            if best_score > 0.5:  # Minimum similarity threshold
                best_category = list(category_examples.keys())[best_idx]
                if best_category in self.category_list:
                    return best_category
                    
            return None
            
        except Exception as e:
            logging.error(f"Embeddings categorization failed: {e}")
            return None

    def _categorize_with_patterns(self, ticket_content):
        """Categorize using pattern matching"""
        text = ticket_content.lower()
        category_scores = {}
        
        for category, config in self.pattern_categorizer.items():
            if category not in self.category_list:
                continue
                
            score = 0
            
            # Check keywords
            for keyword in config["keywords"]:
                if keyword in text:
                    score += 1
            
            # Check patterns (higher weight)
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 2
            
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return category with highest score
            best_category = max(category_scores.items(), key=lambda x: x[1])
            return best_category[0]
            
        return None

    def search_web_for_solution(self, ticket_content, category):
        """
        Search web for solutions using Tavily
        """
        if not self.web_search_enabled or not self.search_client:
            return None
        
        try:
            # Determine search strategy based on category
            if category in ["bug_report", "technical_issue", "troubleshooting"]:
                search_results = self.search_client.search_troubleshooting(ticket_content, category)
            elif category == "documentation":
                search_results = self.search_client.search_documentation(ticket_content)
            else:
                search_results = self.search_client.search_for_solution(ticket_content, category)
            
            return search_results
        except Exception as e:
            logging.error(f"Web search failed: {e}")
            return None

    def generate_solution(self, ticket_content, category, kb_context="", use_web_search=True):
        """Generate solution using available methods including web search"""
        
        # Get web search context if enabled
        web_context = ""
        search_info = ""
        
        if use_web_search and self.web_search_enabled:
            try:
                search_results = self.search_web_for_solution(ticket_content, category)
                if search_results and search_results.get("success"):
                    web_context = create_search_context(search_results)
                    search_info = f"web_search+template (found {len(search_results.get('results', []))} sources)"
                else:
                    search_info = "template (web search failed)"
            except Exception as e:
                logging.warning(f"Web search error: {e}")
                search_info = "template (web search error)"
        else:
            search_info = "template"

        # Generate enhanced solution with all available context
        solution = self._generate_enhanced_solution(
            ticket_content, 
            category, 
            kb_context, 
            web_context
        )
        
        return solution, search_info

    def _generate_enhanced_solution(self, content, category, kb_context, web_context):
        """Generate enhanced solution using all available context"""
        
        # Base template solutions
        templates = {
            "bug_report": "For bug reports, please provide detailed steps to reproduce the issue. Try restarting VS Code and disabling other extensions to isolate the problem.",
            "feature_request": "Thank you for your feature suggestion! We'll consider it for future releases. Check our GitHub repository for similar requests and updates.",
            "performance": "For performance issues, try disabling unused extensions, clearing VS Code cache, and checking Task Manager for resource usage patterns.",
            "authentication": "Verify your credentials are correct and current. Clear cached authentication tokens and check firewall settings that might block authentication requests.",
            "documentation": "Please refer to our official documentation and community guides. Check our GitHub README and wiki pages for comprehensive tutorials.",
            "technical_issue": "Check your installation and configuration settings. Ensure all dependencies are properly installed and VS Code is up to date.",
            "integration": "Review the API documentation and connection settings. Verify API keys, endpoints, and network connectivity requirements.",
            "ui_ux": "Try resetting your workspace settings or updating the extension. Clear VS Code cache and restart the application.",
            "installation": "Ensure you have proper permissions and VS Code is updated. Try installing from VS Code marketplace directly or via command line.",
            "configuration": "Check your settings.json file for syntax errors. Reset to default configuration if needed and reconfigure step by step.",
            "troubleshooting": "Follow systematic debugging steps: check logs, disable extensions, restart VS Code, and verify configurations."
        }
        
        solution = templates.get(category, "Thank you for reaching out. Please provide more details about your issue so we can assist you better.")
        
        if kb_context:
            solution += f"\n\nKnowledge Base Info:\n{kb_context}"

        solution += f"""

---
Professional Support System Response
- Category: {category}
- Analysis Method: Template-based
- Response Quality: Standard

This solution was generated by our AI-powered support system. For additional assistance, please contact our technical support team."""
        
        return solution

    def safe_categorize_ticket(self, ticket_content):
        """Safe wrapper for categorization"""
        try:
            return self.categorize_ticket(ticket_content)
        except Exception as e:
            logging.error(f"Categorization error: {e}")
            return "general_query", "error"

    def safe_generate_solution(self, ticket_content, category, kb_context="", use_web_search=True):
        """Safe wrapper for solution generation with web search option"""
        try:
            return self.generate_solution(ticket_content, category, kb_context, use_web_search)
        except Exception as e:
            logging.error(f"Solution generation error: {e}")
            return self._template_solution(ticket_content, category, kb_context), "error"

    def get_search_status(self):
        """Get current status of web search integration"""
        return {
            "web_search_enabled": self.web_search_enabled,
            "search_client_available": self.search_client is not None,
            "tavily_integration": TAVILY_INTEGRATION
        }

def tavily_search(ticket_content, category=None):
    """
    Perform a Tavily web search for the given ticket content and category.
    Returns a formatted string with web search context, or an error message.
    """
    resolver = MultiModelResolver()
    if not category:
        category, _ = resolver.safe_categorize_ticket(ticket_content)
    results = resolver.search_web_for_solution(ticket_content, category)
    if results and results.get("success"):
        return create_search_context(results)
    elif results and results.get("error"):
        return f"Tavily search error: {results['error']}"
    else:
        return "No Tavily web results found or Tavily integration is not available."


# Test function
def test_categorizer():
    """Test the categorizer with sample tickets"""
    resolver = MultiModelResolver()
    
    test_tickets = [
        "The extension crashes when I open large files",
        "How do I configure the settings?", 
        "Please add dark mode support",
        "Authentication keeps failing",
        "The UI layout is broken"
    ]
    
    print("Testing categorization with Tavily integration:")
    print("=" * 60)
    
    # Show search status
    search_status = resolver.get_search_status()
    print(f"Web Search Status: {search_status}")
    print("-" * 60)
    
    for ticket in test_tickets:
        print(f"\nTicket: {ticket}")
        
        # Test categorization
        category, source = resolver.safe_categorize_ticket(ticket)
        print(f"Category: {category} (source: {source})")
        
        # Test solution generation with web search
        solution, sol_source = resolver.safe_generate_solution(ticket, category, use_web_search=True)
        print(f"Solution Source: {sol_source}")
        print(f"Solution Preview: {solution[:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Support System Resolver & Tavily Search")
    parser.add_argument('--tavily-search', type=str, help='Perform Tavily web search for the given query')
    parser.add_argument('--category', type=str, default=None, help='Optional category for Tavily search')
    parser.add_argument('--test', action='store_true', help='Run categorizer and solution tests')
    args = parser.parse_args()

    if args.tavily_search:
        print("\n=== Tavily Web Search ===")
        result = tavily_search(args.tavily_search, category=args.category)
        print(result)
    elif args.test:
        test_categorizer()
    else:
        parser.print_help()

__all__ = ["MultiModelResolver"]