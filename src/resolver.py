import logging
import os
from typing import Tuple, Optional
from transformers import pipeline
import google.generativeai as genai
from openai import OpenAI
from tavily import TavilyClient
import re

# Use the richer rule-based categorizer if available
try:
    from ticket_categorization import TicketCategorizer  # type: ignore
    _CATEGORIZER = TicketCategorizer()
except Exception:
    _CATEGORIZER = None

logger = logging.getLogger(__name__)

def clean_hf_response(text: str) -> str:
    """Clean Hugging Face fallback responses."""
    lines = text.splitlines()
    unique_lines = []
    for line in lines:
        if line.strip() and line not in unique_lines:
            unique_lines.append(line)
    text = "\n".join(unique_lines)
    text = re.sub(r"http[s]?://[^\s]+", "[link removed]", text)
    if "Ubuntu" in text and "Windows" in text:
        text += "\n\n(Note: Mixed OS references may exist. Verify your system.)"
    return text.strip()

def tavily_search(query: str) -> str:
    """Perform a Tavily web search and return a concise answer."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "(No Tavily API key set. Please export TAVILY_API_KEY before running.)"
    
    try:
        client = TavilyClient(api_key=api_key)
        result = client.qna_search(query)
        return result.get("answer", "No relevant results found")
    except Exception as e:
        logging.error(f"Tavily search error: {e}")
        return f"(Tavily search error: {e})"


class MultiModelResolver:
    def __init__(self, knowledge_base: Optional[dict] = None, provider: str = None, enable_web_search: bool = False):
        self.knowledge_base = knowledge_base or {}
        self.provider = provider or "keyword"
        self.web_search_enabled = enable_web_search
        self.search_client = None
        logging.info(f"MultiModelResolver initialized provider={self.provider} web_search={self.web_search_enabled}")

        if self.web_search_enabled:
            try:
                from tavily_client import TavilySearchClient  # type: ignore
                self.search_client = TavilySearchClient()
            except Exception:
                self.search_client = None

    # -----------------------------
    # KB coverage
    # -----------------------------
    def check_kb_coverage(self, category: str):
        logger.debug(f"Available KB categories: {list(self.knowledge_base.keys())}")
        if category in self.knowledge_base:
            print(f"✅ KB entry found for '{category}'")
        else:
            print(f"❌ No KB entry for '{category}'")
            logger.warning(f"Missing KB entry for '{category}'")

    # -----------------------------
    # Ticket categorization
    # -----------------------------
    def categorize_ticket(self, ticket: str) -> Tuple[str, str]:
        logging.info(f"[categorize_ticket] Categorizing ticket: {ticket}")
        if _CATEGORIZER:
            try:
                category, confidence, _ = _CATEGORIZER.categorize_ticket(ticket)
                return category.strip().lower().replace(" ", "_"), "pattern"
            except Exception as e:
                logger.error(f"Rule-based categorization failed: {e}")
        if self.provider == "gemini":
            return self._llm_categorize_gemini(ticket)
        return self._keyword_categorize(ticket)

    def safe_categorize_ticket(self, ticket: str) -> Tuple[str, str]:
        """Safe wrapper for categorization."""
        try:
            return self.categorize_ticket(ticket)
        except Exception as e:
            logging.error(f"Categorization error: {e}")
            return "general_query", "error"

    def _keyword_categorize(self, text: str) -> Tuple[str, str]:
        text = text.lower()
        if "login" in text or "password" in text:
            return "login_issue", "pattern"
        elif "error" in text or "bug" in text:
            return "bug_report", "pattern"
        elif "feature" in text or "request" in text:
            return "feature_request", "pattern"
        elif "network" in text or "connection" in text:
            return "network_error", "pattern"
        else:
            return "general_query", "pattern"

    def _llm_categorize_gemini(self, ticket: str) -> Tuple[str, str]:
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            prompt = (
                "Classify this support ticket into one category: "
                "login_issue, bug_report, feature_request, network_error, general_query.\n\n"
                f"Ticket: {ticket}"
            )
            response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
            category = response.text.strip().lower().replace(" ", "_")
            return category, "gemini"
        except Exception as e:
            logging.error(f"Gemini categorization error: {e}")
            return self._keyword_categorize(ticket)

    # -----------------------------
    # Solution generation
    # -----------------------------
    def _kb_first_compose(self, kb_context: str, user_query: str) -> str:
        lines = [l.strip(" -•\t") for l in kb_context.splitlines() if l.strip()]
        steps = []
        for line in lines:
            if any(k in line.lower() for k in ["install", "run", "open", "click", "use", "publish", "login", "configure", "set"]):
                steps.append(line)
            if len(steps) >= 5:
                break
        if not steps:
            preview = kb_context[:280].replace("\n", " ")
            return f"Summary: {preview}"
        numbered = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
        return f"Brief diagnosis for '{user_query[:60]}':\n{numbered}"

    def _format_chat_style(self, body: str, category: str, method: str, quality: str) -> str:
        cleaned = re.sub(r"\s+", " ", body).strip()
        if len(cleaned) > 900:
            cleaned = cleaned[:900].rstrip() + "..."
        return (
            f"Professional Support System Response\n"
            f"- Category: {category}\n"
            f"- Analysis Method: {method}\n"
            f"- Response Quality: {quality}\n\n"
            f"Suggested Solution:\n{cleaned}\n\n"
            f"This solution was generated by our AI-powered support system."
        )

    def _generate_enhanced_solution(self, ticket: str, category: str, method: str, platform: str = "VS Code") -> Tuple[str, str]:
        logging.info(f"[EnhancedSolution] Ticket category: {category} | Platform: {platform}")

        # 1️⃣ Knowledge Base Lookup
        kb_solution = self.knowledge_base.get(category)
        if kb_solution:
            if isinstance(kb_solution, dict):
                kb_solution = kb_solution.get(platform, None) or next(iter(kb_solution.values()))
            if kb_solution:
                return self._format_chat_style(kb_solution, category, method, "Knowledge Base (Platform-aware)"), "Knowledge Base"

        # 2️⃣ LLM Reasoning (Gemini/OpenAI)
        if self.provider.lower() == "gemini":
            try:
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                prompt = f"""
                You are a support assistant for {platform}.
                A user asked: "{ticket}"
                Provide a clear, actionable, and platform-specific solution.
                """
                response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
                llm_solution = response.text.strip()
                if llm_solution:
                    return self._format_chat_style(llm_solution, category, "Gemini LLM", "AI-generated (Platform-aware)"), "Gemini LLM"
            except Exception as e:
                logging.warning(f"Gemini LLM failed: {e}")

        # 3️⃣ Hugging Face Fallback
        try:
            hf_model = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")
            hf_prompt = f"""
            You are a support assistant for {platform}.
            A user asked: "{ticket}"
            Provide a helpful, accurate, and platform-specific response for {platform} only.
            """
            hf_response = hf_model(hf_prompt, max_new_tokens=200, truncation=True)[0]["generated_text"]
            hf_solution = clean_hf_response(hf_response)
            if hf_solution:
                return self._format_chat_style(hf_solution, category, "Hugging Face", "AI Fallback (Platform-aware)"), "Hugging Face"
        except Exception as e:
            logging.warning(f"Hugging Face fallback failed: {e}")

        # 4️⃣ Template Fallback
        templates = {
            "login_issue": f"Use 'Forgot Password' to reset. Contact support if it fails on {platform}.",
            "bug_report": f"Provide steps to reproduce the bug and any error messages for {platform}.",
            "feature_request": f"Thanks for the suggestion! We will review it for {platform}.",
            "network_error": f"Check your connection and restart your router. Ensure {platform} settings are correct.",
        }
        template_solution = templates.get(category, f"Steps for {category} on {platform}: check settings and escalate if needed.")
        return self._format_chat_style(template_solution, category, "Template Fallback", "Structured Template"), "Template"


    def safe_generate_solution(self, ticket: str, platform: str = "VS Code"):
        category, method = self.safe_categorize_ticket(ticket)
        return self._generate_enhanced_solution(ticket, category, method, platform)

    def generate_solution(self, ticket: str):
        return self.safe_generate_solution(ticket)



    def get_search_status(self):
        return {
            "web_search_enabled": self.web_search_enabled,
            "search_client_available": self.search_client is not None,
        }

    def search_web_for_solution(self, query: str, category: Optional[str] = None):
        if not (self.web_search_enabled and self.search_client):
            return {"success": False, "error": "Web search disabled or unavailable"}
        try:
            result = self.search_client.search(query)
            return {"success": True, **(result or {})}
        except Exception as e:
            return {"success": False, "error": str(e)}


# -----------------------------
# CLI / Test Harness
# -----------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_kb = {
        "login_issue": "Use 'Forgot Password' to reset. Contact support if it fails.",
        "ui_customization": "Edit the theme CSS file in /static/css/theme.css and restart the server. Clear browser cache after changes."
    }
    resolver = MultiModelResolver(knowledge_base=example_kb)

    cat, method = resolver.safe_categorize_ticket("I cannot login with my password!")
    print("Category:", cat, "Method:", method)

    sol, src = resolver.safe_generate_solution("I cannot login with my password!")
    print("Solution source:", src)
    print(sol)
