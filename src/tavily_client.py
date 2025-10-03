"""
Tavily Search Integration for AI Support System
Provides web search capabilities for enhanced solution generation
"""

import os
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logging.warning("Tavily not installed. Install with: pip install tavily-python")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TavilySearchClient:
    """
    Tavily search client for enhanced support ticket resolution
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily client
        
        Args:
            api_key: Tavily API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.client = None
        self.search_enabled = False
        
        if not TAVILY_AVAILABLE:
            logger.error("Tavily package not available. Web search will be disabled.")
            return
            
        if not self.api_key:
            logger.warning("No Tavily API key found. Set TAVILY_API_KEY environment variable.")
            return
            
        try:
            self.client = TavilyClient(api_key=self.api_key)
            self.search_enabled = True
            logger.info("Tavily search client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Tavily client: {e}")
    
    def is_available(self) -> bool:
        """Check if Tavily search is available"""
        return self.search_enabled and self.client is not None
    
    def search_for_solution(
        self, 
        query: str, 
        category: str = "general",
        max_results: int = 3,
        include_domains: Optional[List[str]] = None
    ) -> Dict:
        """
        Search for solutions related to the ticket query
        
        Args:
            query: The search query (ticket content)
            category: Ticket category for context
            max_results: Maximum number of results to return
            include_domains: Specific domains to search (optional)
            
        Returns:
            Dict with search results and metadata
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Tavily search not available",
                "results": [],
                "search_query": query
            }
        
        try:
            # Enhance query with category context
            enhanced_query = self._enhance_query(query, category)
            
            search_params = {
                "query": enhanced_query,
                "search_depth": "basic",
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": False
            }
            
            # Add domain filtering if specified
            if include_domains:
                search_params["include_domains"] = include_domains
            
            logger.info(f"Searching Tavily for: {enhanced_query}")
            response = self.client.search(**search_params)
            
            # Process and format results
            processed_results = self._process_search_results(response)
            
            return {
                "success": True,
                "search_query": enhanced_query,
                "original_query": query,
                "category": category,
                "results": processed_results,
                "answer": response.get("answer", ""),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "search_query": query
            }
    
    def _enhance_query(self, query: str, category: str) -> str:
        """
        Enhance search query with category-specific context
        """
        category_contexts = {
            "bug_report": "VS Code extension bug error fix solution",
            "feature_request": "VS Code extension feature implementation guide",
            "technical_issue": "VS Code extension technical problem troubleshooting",
            "documentation": "VS Code extension documentation guide tutorial",
            "performance": "VS Code extension performance optimization speed",
            "authentication": "VS Code extension authentication login fix",
            "integration": "VS Code extension API integration setup",
            "ui_ux": "VS Code extension UI interface problem fix",
            "installation": "VS Code extension installation setup guide",
            "configuration": "VS Code extension configuration settings",
            "troubleshooting": "VS Code extension troubleshooting debug fix"
        }
        
        context = category_contexts.get(category, "VS Code extension")
        enhanced_query = f"{context} {query}"
        
        return enhanced_query
    
    def _process_search_results(self, response: Dict) -> List[Dict]:
        """
        Process and format Tavily search results
        """
        results = []
        
        if "results" not in response:
            return results
        
        for result in response["results"]:
            processed_result = {
                "title": result.get("title", "No Title"),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0),
                "published_date": result.get("published_date", ""),
                "relevance": self._calculate_relevance(result)
            }
            
            # Clean and truncate content
            processed_result["content"] = self._clean_content(processed_result["content"])
            results.append(processed_result)
        
        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def _clean_content(self, content: str, max_length: int = 500) -> str:
        """
        Clean and truncate content for display
        """
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = " ".join(content.split())
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content
    
    def _calculate_relevance(self, result: Dict) -> float:
        """
        Calculate relevance score for a search result
        """
        relevance = result.get("score", 0)
        
        # Boost results from known technical domains
        url = result.get("url", "").lower()
        technical_domains = [
            "stackoverflow.com",
            "github.com", 
            "code.visualstudio.com",
            "marketplace.visualstudio.com",
            "docs.microsoft.com"
        ]
        
        for domain in technical_domains:
            if domain in url:
                relevance += 0.2
                break
        
        return min(relevance, 1.0)  # Cap at 1.0
    
    def search_documentation(
        self, 
        topic: str, 
        product: str = "VS Code extension"
    ) -> Dict:
        """
        Search specifically for documentation
        """
        query = f"{product} {topic} documentation official guide"
        
        include_domains = [
            "code.visualstudio.com",
            "docs.microsoft.com", 
            "github.com",
            "marketplace.visualstudio.com"
        ]
        
        return self.search_for_solution(
            query=query,
            category="documentation",
            max_results=3,
            include_domains=include_domains
        )
    
    def search_troubleshooting(
        self, 
        error_description: str,
        category: str = "bug_report"
    ) -> Dict:
        """
        Search specifically for troubleshooting information
        """
        query = f"VS Code extension {error_description} fix solution troubleshooting"
        
        include_domains = [
            "stackoverflow.com",
            "github.com",
            "code.visualstudio.com"
        ]
        
        return self.search_for_solution(
            query=query,
            category=category,
            max_results=5,
            include_domains=include_domains
        )
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """
        Generate search query suggestions based on the input
        """
        base_suggestions = [
            f"VS Code extension {query}",
            f"{query} troubleshooting guide",
            f"{query} documentation",
            f"how to fix {query}",
            f"{query} best practices"
        ]
        
        return base_suggestions

# Utility functions for integration
def create_search_context(search_results: Dict) -> str:
    """
    Create formatted context from search results for AI solution generation
    """
    if not search_results.get("success") or not search_results.get("results"):
        return ""
    
    context_parts = []
    
    # Add Tavily's AI answer if available
    if search_results.get("answer"):
        context_parts.append(f"Web Search Summary: {search_results['answer']}")
    
    # Add top search results
    context_parts.append("\nRelevant Web Sources:")
    for i, result in enumerate(search_results["results"][:3], 1):
        title = result["title"]
        content = result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
        url = result["url"]
        
        context_parts.append(f"{i}. {title}")
        context_parts.append(f"   Source: {url}")
        context_parts.append(f"   Content: {content}")
        context_parts.append("")
    
    return "\n".join(context_parts)

def test_tavily_search():
    """
    Test function for Tavily search integration
    """
    client = TavilySearchClient()
    
    if not client.is_available():
        print("Tavily search not available. Check API key and installation.")
        return
    
    test_queries = [
        ("VS Code extension crashes on startup", "bug_report"),
        ("How to add custom commands to extension", "feature_request"),
        ("Extension authentication with GitHub", "authentication")
    ]
    
    print("Testing Tavily Search Integration:")
    print("=" * 50)
    
    for query, category in test_queries:
        print(f"\nQuery: {query}")
        print(f"Category: {category}")
        print("-" * 30)
        
        results = client.search_for_solution(query, category, max_results=2)
        
        if results["success"]:
            print(f"Search Query Used: {results['search_query']}")
            if results.get("answer"):
                print(f"AI Answer: {results['answer'][:200]}...")
            
            print(f"Found {len(results['results'])} results:")
            for i, result in enumerate(results["results"], 1):
                print(f"  {i}. {result['title']}")
                print(f"     {result['url']}")
                print(f"     Score: {result['score']:.2f}")
        else:
            print(f"Search failed: {results.get('error')}")
        
        print()

if __name__ == "__main__":
    test_tavily_search()