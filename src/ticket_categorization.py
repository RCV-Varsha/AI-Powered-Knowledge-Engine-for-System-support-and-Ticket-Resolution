# ticket_categorization.py
"""
AI-powered ticket categorization system for VS Code extension support
"""

import re
from typing import Dict, List, Tuple
import json

class TicketCategorizer:
    """AI-powered ticket categorization system"""
    
    def __init__(self):
        # Define categories with keywords and patterns
        self.categories = {
            "Bug Report": {
                "keywords": ["bug", "error", "crash", "broken", "not working", "issue", "problem", 
                            "exception", "fail", "doesn't work", "stopped working", "malfunction"],
                "patterns": [r"error.*code", r"crash.*when", r"doesn't.*work", r"not.*working",
                           r"throws.*error", r"getting.*error"]
            },
            "Feature Request": {
                "keywords": ["feature", "request", "suggestion", "enhance", "improvement", "add", 
                            "new", "would like", "wish", "could you", "please add", "enhancement"],
                "patterns": [r"would.*like", r"could.*you.*add", r"please.*add", r"feature.*request",
                           r"suggestion.*for", r"enhance.*with"]
            },
            "Technical Issue": {
                "keywords": ["install", "installation", "setup", "configure", "configuration", 
                            "permission", "access", "compatibility", "version", "update", "upgrade"],
                "patterns": [r"how.*to.*install", r"setup.*issue", r"configuration.*problem",
                           r"compatibility.*with", r"version.*conflict"]
            },
            "Documentation": {
                "keywords": ["documentation", "docs", "guide", "tutorial", "help", "how to", 
                            "example", "usage", "manual", "instructions", "readme"],
                "patterns": [r"how.*to.*use", r"where.*is.*documentation", r"need.*help.*with",
                           r"tutorial.*for", r"guide.*on"]
            },
            "Performance": {
                "keywords": ["slow", "performance", "speed", "lag", "memory", "cpu", "optimization",
                            "freeze", "hang", "timeout", "delay", "takes forever"],
                "patterns": [r"runs.*slow", r"performance.*issue", r"takes.*long.*time",
                           r"memory.*usage", r"cpu.*high"]
            },
            "Integration": {
                "keywords": ["integration", "api", "webhook", "connect", "sync", "import", "export",
                            "third party", "external", "plugin", "extension compatibility"],
                "patterns": [r"integrate.*with", r"connect.*to", r"api.*not.*working",
                           r"sync.*with", r"import.*from"]
            },
            "UI/UX": {
                "keywords": ["interface", "ui", "ux", "design", "layout", "theme", "color", "font",
                            "button", "menu", "display", "visual", "appearance"],
                "patterns": [r"ui.*issue", r"interface.*problem", r"design.*bug",
                           r"layout.*broken", r"display.*incorrect"]
            },
            "Authentication": {
                "keywords": ["login", "authentication", "auth", "password", "credentials", "token",
                            "oauth", "signin", "sign in", "account", "access denied"],
                "patterns": [r"login.*fail", r"authentication.*error", r"access.*denied",
                           r"credentials.*invalid", r"token.*expired"]
            }
        }
        
        # Category priority (higher priority categories checked first)
        self.category_priority = [
            "Authentication", "Bug Report", "Technical Issue", "Performance", 
            "Integration", "Feature Request", "UI/UX", "Documentation"
        ]
    
    def categorize_ticket(self, content: str, title: str = "") -> Tuple[str, float, Dict]:
        """
        Categorize a ticket based on content and title
        
        Args:
            content: The ticket content/description
            title: Optional ticket title
            
        Returns:
            Tuple of (category, confidence_score, analysis_details)
        """
        if not content and not title:
            return "Other", 0.0, {"reason": "No content provided"}
        
        # Combine title and content for analysis
        full_text = f"{title} {content}".lower().strip()
        
        category_scores = {}
        analysis_details = {"matched_keywords": {}, "matched_patterns": {}}
        
        # Score each category
        for category in self.category_priority:
            score = self._calculate_category_score(full_text, category, analysis_details)
            if score > 0:
                category_scores[category] = score
        
        # Determine best category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            category, confidence = best_category
            
            # Normalize confidence to 0-1 scale
            normalized_confidence = min(confidence / 10.0, 1.0)
            
            return category, normalized_confidence, analysis_details
        
        return "Other", 0.0, {"reason": "No matching patterns found"}
    
    def _calculate_category_score(self, text: str, category: str, analysis_details: Dict) -> float:
        """Calculate score for a specific category"""
        score = 0.0
        category_data = self.categories[category]
        
        # Check keywords
        matched_keywords = []
        for keyword in category_data["keywords"]:
            if keyword in text:
                score += 1.0
                matched_keywords.append(keyword)
        
        if matched_keywords:
            analysis_details["matched_keywords"][category] = matched_keywords
        
        # Check patterns (higher weight)
        matched_patterns = []
        for pattern in category_data["patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += 2.0  # Patterns get higher weight
                matched_patterns.extend(matches)
        
        if matched_patterns:
            analysis_details["matched_patterns"][category] = matched_patterns
        
        return score
    
    def get_category_suggestions(self, content: str, title: str = "", top_n: int = 3) -> List[Dict]:
        """Get top N category suggestions with confidence scores"""
        if not content and not title:
            return []
        
        full_text = f"{title} {content}".lower().strip()
        category_scores = []
        
        for category in self.categories.keys():
            analysis_details = {"matched_keywords": {}, "matched_patterns": {}}
            score = self._calculate_category_score(full_text, category, analysis_details)
            
            if score > 0:
                normalized_confidence = min(score / 10.0, 1.0)
                category_scores.append({
                    "category": category,
                    "confidence": normalized_confidence,
                    "score": score,
                    "analysis": analysis_details
                })
        
        # Sort by score and return top N
        category_scores.sort(key=lambda x: x["score"], reverse=True)
        return category_scores[:top_n]

# Integration with sheets
def categorize_and_update_ticket(ticket_content: str, ticket_title: str = "") -> Dict:
    """
    Categorize a ticket and return the result
    """
    categorizer = TicketCategorizer()
    category, confidence, analysis = categorizer.categorize_ticket(ticket_content, ticket_title)
    
    return {
        "category": category,
        "confidence": confidence,
        "analysis": analysis,
        "suggestions": categorizer.get_category_suggestions(ticket_content, ticket_title)
    }

# Demo function
def demo_categorization():
    """Demo the categorization system"""
    
    print("=" * 60)
    print("🤖 TICKET CATEGORIZATION DEMO")
    print("=" * 60)
    
    # Test cases representing common VS Code extension support tickets
    test_tickets = [
        {
            "title": "Extension crashes when opening large files",
            "content": "The VS Code extension crashes whenever I try to open files larger than 100MB. Getting error code 500."
        },
        {
            "title": "Feature request: Auto-completion",
            "content": "Would like to add auto-completion feature for custom file types. This would enhance productivity."
        },
        {
            "title": "Installation issues",
            "content": "Having trouble installing the extension. Getting permission errors during setup process."
        },
        {
            "title": "Need documentation",
            "content": "Where can I find documentation on how to use the advanced features? Need examples and tutorials."
        },
        {
            "title": "Performance problems",
            "content": "The extension is running very slow and consuming too much memory. Takes forever to load."
        },
        {
            "title": "Login not working",
            "content": "Authentication failed. Can't login with my credentials. Getting access denied error."
        },
        {
            "title": "API integration",
            "content": "How do I integrate this extension with external APIs? Need to connect to third party services."
        },
        {
            "title": "UI layout broken",
            "content": "The interface layout is completely broken after the last update. Buttons are not visible."
        }
    ]
    
    categorizer = TicketCategorizer()
    
    for i, ticket in enumerate(test_tickets, 1):
        print(f"\n{i}. Testing Ticket:")
        print(f"   Title: {ticket['title']}")
        print(f"   Content: {ticket['content'][:60]}...")
        
        # Get categorization
        category, confidence, analysis = categorizer.categorize_ticket(
            ticket['content'], ticket['title']
        )
        
        print(f"   🎯 Category: {category}")
        print(f"   📊 Confidence: {confidence:.2f}")
        
        if analysis.get("matched_keywords"):
            for cat, keywords in analysis["matched_keywords"].items():
                print(f"   🔍 Keywords ({cat}): {', '.join(keywords[:3])}")
        
        # Show top suggestions
        suggestions = categorizer.get_category_suggestions(
            ticket['content'], ticket['title'], top_n=2
        )
        
        if len(suggestions) > 1:
            print(f"   💡 Alternative: {suggestions[1]['category']} ({suggestions[1]['confidence']:.2f})")
    
    print("\n" + "=" * 60)
    print("✅ CATEGORIZATION DEMO COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    demo_categorization()