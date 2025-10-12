"""
Article suggestion engine with usage tracking and analytics
"""

import json
from pathlib import Path
from datetime import datetime
from kb_processor import load_kb_retriever
import logging

from faiss_retriever import get_faiss_retriever
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# -----------------------------
# New function: AI-powered solution
# -----------------------------
def get_ai_solution(ticket_text):
    # Load FAISS retriever
    retriever = get_faiss_retriever(k=5)
    if not retriever:
        return "❌ KB retriever not ready. Try again later."

    # Build RAG chain
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    # Run query and get answer
    answer = qa_chain.run(ticket_text)
    return answer


# Logging setup
logging.basicConfig(level=logging.INFO)

# Analytics tracking files
ARTICLE_LOG_PATH = Path("article_usage_log.jsonl")
TICKET_LOG_PATH = Path("ticket_log.jsonl")

def suggest_articles(ticket_text, top_k=5):
    retriever = load_kb_retriever()
    if not retriever:
        logging.warning("Knowledge base retriever not available")
        return []

    try:
        results = retriever.invoke(ticket_text)  # or retriever.get_relevant_documents(ticket_text)
        
        seen_sources = set()
        top_results = []
        for doc in results:
            source = doc.metadata.get('source', 'unknown')
            if source not in seen_sources:
                top_results.append(doc)
                seen_sources.add(source)
            if len(top_results) >= top_k:
                break

        _log_article_usage(ticket_text, top_results)
        return top_results
    except Exception as e:
        logging.error(f"Error suggesting articles: {e}")
        return []

def _log_article_usage(ticket_text, suggested_articles):
    """Log article suggestions for analytics tracking"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ticket_text": ticket_text[:200],
            "suggested_articles": [
                {
                    "source": doc.metadata.get('source', 'unknown'),
                    "content_preview": doc.page_content[:100],
                }
                for doc in suggested_articles
            ],
            "num_suggestions": len(suggested_articles)
        }
        
        with open(ARTICLE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logging.error(f"Error logging article usage: {e}")

def log_ticket_resolution(ticket_id, ticket_content, category, solution, 
                         suggested_articles, user_satisfied, resolution_time=None):
    """Log ticket resolution details for analytics"""
    try:
        log_entry = {
            "ticket_id": ticket_id,
            "timestamp": datetime.now().isoformat(),
            "ticket_content": ticket_content[:200],
            "category": category,
            "solution_preview": solution[:300],
            "suggested_articles": [
                get_article_title(doc) if hasattr(doc, 'page_content') else str(doc)
                for doc in suggested_articles
            ],
            "user_satisfied": user_satisfied,
            "resolution_time_seconds": resolution_time,
            "feedback_type": "positive" if user_satisfied else "negative"
        }
        
        with open(TICKET_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logging.error(f"Error logging ticket resolution: {e}")

def get_article_title(doc):
    """Extract a meaningful title from a document"""
    if hasattr(doc, 'metadata') and 'source' in doc.metadata:
        return Path(doc.metadata['source']).stem
    elif hasattr(doc, 'page_content'):
        first_line = doc.page_content.split('\n')[0].strip()
        return first_line[:40] + "..." if len(first_line) > 40 else first_line
    else:
        return str(doc)[:40] + "..."

def get_article_analytics():
    """Get analytics about article usage and effectiveness"""
    analytics = {
        "total_suggestions": 0,
        "most_suggested_articles": {},
        "satisfaction_by_article": {},
        "category_article_mapping": {},
        "articles_needing_improvement": []
    }
    
    try:
        # Load article usage log
        if ARTICLE_LOG_PATH.exists():
            with open(ARTICLE_LOG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    analytics["total_suggestions"] += entry.get("num_suggestions", 0)
                    
                    for article in entry.get("suggested_articles", []):
                        source = article.get("source", "unknown")
                        analytics["most_suggested_articles"][source] = \
                            analytics["most_suggested_articles"].get(source, 0) + 1
        
        # Load ticket resolution log
        if TICKET_LOG_PATH.exists():
            with open(TICKET_LOG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    category = entry.get("category", "unknown")
                    satisfied = entry.get("user_satisfied", False)
                    articles = entry.get("suggested_articles", [])
                    
                    for article in articles:
                        if article not in analytics["satisfaction_by_article"]:
                            analytics["satisfaction_by_article"][article] = {
                                "total": 0, "satisfied": 0
                            }
                        analytics["satisfaction_by_article"][article]["total"] += 1
                        if satisfied:
                            analytics["satisfaction_by_article"][article]["satisfied"] += 1
                    
                    if category not in analytics["category_article_mapping"]:
                        analytics["category_article_mapping"][category] = {}
                    for article in articles:
                        analytics["category_article_mapping"][category][article] = \
                            analytics["category_article_mapping"][category].get(article, 0) + 1
        
        # Identify articles needing improvement
        for article, stats in analytics["satisfaction_by_article"].items():
            if stats["total"] >= 3:
                satisfaction_rate = stats["satisfied"] / stats["total"]
                if satisfaction_rate < 0.5:
                    analytics["articles_needing_improvement"].append({
                        "article": article,
                        "satisfaction_rate": satisfaction_rate,
                        "total_uses": stats["total"]
                    })
        
        analytics["most_suggested_articles"] = dict(
            sorted(analytics["most_suggested_articles"].items(), 
                   key=lambda x: x[1], reverse=True)
        )
        
        analytics["articles_needing_improvement"].sort(
            key=lambda x: x["satisfaction_rate"]
        )
        
    except Exception as e:
        logging.error(f"Error generating analytics: {e}")
    
    return analytics

def get_content_gaps():
    """Identify content gaps"""
    gaps = {
        "low_coverage_topics": [],
        "frequent_unsatisfied_queries": [],
        "suggested_new_articles": []
    }
    
    try:
        if not TICKET_LOG_PATH.exists():
            return gaps
        
        unsatisfied_categories = {}
        unsatisfied_keywords = {}
        
        with open(TICKET_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if not entry.get("user_satisfied", False):
                    category = entry.get("category", "unknown")
                    unsatisfied_categories[category] = unsatisfied_categories.get(category, 0) + 1
                    
                    content = entry.get("ticket_content", "").lower()
                    words = content.split()
                    for word in words:
                        if len(word) > 4 and word.isalpha():
                            unsatisfied_keywords[word] = unsatisfied_keywords.get(word, 0) + 1
        
        gaps["low_coverage_topics"] = [
            {"category": cat, "unsatisfied_count": count}
            for cat, count in sorted(unsatisfied_categories.items(), 
                                   key=lambda x: x[1], reverse=True)[:5]
        ]
        
        gaps["frequent_unsatisfied_queries"] = [
            {"keyword": word, "frequency": count}
            for word, count in sorted(unsatisfied_keywords.items(), 
                                    key=lambda x: x[1], reverse=True)[:10]
        ]
        
        for topic in gaps["low_coverage_topics"]:
            gaps["suggested_new_articles"].append({
                "topic": topic["category"],
                "priority": "high" if topic["unsatisfied_count"] > 5 else "medium",
                "description": f"Create comprehensive guide for {topic['category']} issues"
            })
    
    except Exception as e:
        logging.error(f"Error analyzing content gaps: {e}")
    
    return gaps

def generate_improvement_alerts():
    """Generate alerts for content that needs improvement"""
    alerts = []
    
    try:
        analytics = get_article_analytics()
        gaps = get_content_gaps()
        
        for article_info in analytics.get("articles_needing_improvement", []):
            alerts.append({
                "type": "low_satisfaction",
                "priority": "high",
                "article": article_info["article"],
                "message": f"Article '{article_info['article']}' has {article_info['satisfaction_rate']:.1%} satisfaction rate",
                "action": "Review and improve article content"
            })
        
        for gap in gaps.get("low_coverage_topics", [])[:3]:
            alerts.append({
                "type": "content_gap",
                "priority": "medium",
                "topic": gap["category"],
                "message": f"High number of unsatisfied tickets in '{gap['category']}' category",
                "action": "Consider creating new articles for this topic"
            })
        
        satisfaction_data = analytics.get("satisfaction_by_article", {})
        most_suggested = analytics.get("most_suggested_articles", {})
        
        for article, suggestion_count in list(most_suggested.items())[:5]:
            if article in satisfaction_data:
                stats = satisfaction_data[article]
                if stats["total"] >= 5 and stats["satisfied"] / stats["total"] < 0.6:
                    alerts.append({
                        "type": "popular_but_ineffective",
                        "priority": "high", 
                        "article": article,
                        "message": f"Popular article '{article}' but only {stats['satisfied']}/{stats['total']} users satisfied",
                        "action": "Priority review needed - article is often suggested but not helpful"
                    })
    
    except Exception as e:
        logging.error(f"Error generating improvement alerts: {e}")
    
    return alerts

def clear_analytics_data():
    """Clear analytics data files"""
    try:
        if ARTICLE_LOG_PATH.exists():
            ARTICLE_LOG_PATH.unlink()
        if TICKET_LOG_PATH.exists():
            TICKET_LOG_PATH.unlink()
        logging.info("Analytics data cleared")
        return True
    except Exception as e:
        logging.error(f"Error clearing analytics data: {e}")
        return False