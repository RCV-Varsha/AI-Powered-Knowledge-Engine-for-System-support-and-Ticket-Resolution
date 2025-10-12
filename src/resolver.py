import logging
import os
from typing import Tuple, Optional
from transformers import pipeline

import google.generativeai as genai
from openai import OpenAI
from tavily import TavilyClient
import re

# Use the richer rule-based categorizer
try:
    from ticket_categorization import TicketCategorizer  # type: ignore
    _CATEGORIZER = TicketCategorizer()
except Exception:
    _CATEGORIZER = None

def clean_hf_response(text: str) -> str:
    # Remove repeated lines
    lines = text.splitlines()
    unique_lines = []
    for line in lines:
        if line.strip() and line not in unique_lines:
            unique_lines.append(line)
    text = "\n".join(unique_lines)

    # Remove suspicious links
    text = re.sub(r"http[s]?://[^\s]+", "[link removed]", text)

    # Flag mixed OS references
    if "Ubuntu" in text and "Windows" in text:
        text += "\n\n(Note: This response may contain mixed OS references. Please verify your system.)"

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
    def __init__(
        self,
        knowledge_base: Optional[dict] = None,
        provider: str = None,
        enable_web_search: bool = False,
    ):
        """
        Initialize resolver with optional knowledge base.
        provider can be: 'keyword', 'gemini'.
        enable_web_search toggles optional Tavily enrichment (best-effort only).
        """
        self.knowledge_base = knowledge_base or {}
        self.provider = provider or "keyword"
        self.web_search_enabled = bool(enable_web_search)
        self.search_client = None
        try:
            # Lazy import; dashboard/main might not have tavily configured
            from tavily_client import TavilySearchClient  # type: ignore
            if self.web_search_enabled:
                self.search_client = TavilySearchClient()
        except Exception:
            self.search_client = None
        logging.info(
            "MultiModelResolver initialized provider=%s web_search=%s",
            self.provider,
            self.web_search_enabled,
        )

    # -----------------------------
    # Ticket Categorization
    # -----------------------------
    def categorize_ticket(self, ticket: str) -> Tuple[str, str]:
        """Categorize a ticket using a robust rule-based model with optional LLM fallback."""
        # Prefer detailed rule-based categorizer when available
        if _CATEGORIZER is not None:
            try:
                category, confidence, _ = _CATEGORIZER.categorize_ticket(ticket)
                # Normalize to snake_case categories used downstream
                normalized = category.strip().lower().replace(" ", "_")
                return normalized, "pattern"
            except Exception:
                pass

        if self.provider == "gemini":
            return self._llm_categorize_gemini(ticket)
        # Fallback simple keyword categorizer
        return self._keyword_categorize(ticket)

    def safe_categorize_ticket(self, ticket: str) -> Tuple[str, str]:
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
            logging.error("Gemini categorization error: %s", e)
            return self._keyword_categorize(ticket)

    # -----------------------------
    # Solution Generation
    # -----------------------------
    def generate_solution(self, ticket: str):
        # Backward-compatible wrapper that defers to enhanced pipeline without extra context
        category, method = self.safe_categorize_ticket(ticket)
        return self._generate_enhanced_solution(ticket, category, method)

    def safe_generate_solution(
        self,
        ticket: str,
        category: Optional[str] = None,
        kb_context: Optional[str] = None,
        use_web_search: bool = False,
    ):
        """
        Safe wrapper for solution generation.
        Accepts optional category and KB/web context. Always returns (solution_text, source).
        """
        try:
            if not category:
                category, method = self.safe_categorize_ticket(ticket)
            else:
                method = self.provider

            # Optionally enrich with web search (best-effort; non-blocking)
            web_context = ""
            if use_web_search and self.web_search_enabled and self.search_client:
                try:
                    search = self.search_client.search(ticket)
                    if search and search.get("answer"):
                        web_context = f"\n\n[Web Search]\n{search['answer']}"
                except Exception as e:
                    logging.warning(f"Web search enrichment failed: {e}")

            merged_ticket = ticket
            if kb_context or web_context:
                merged_ticket = f"{ticket}\n\n[Context]\n{(kb_context or '').strip()}{web_context}"

            return self._generate_enhanced_solution(merged_ticket, category, method)
        except Exception as e:
            logging.error(f"Solution generation error: {e}")
            return (
                "Professional Support System Response\n"
                "- Category: general_query\n"
                "- Analysis Method: error_fallback\n"
                "- Response Quality: Minimal\n\n"
                "We encountered an error while generating a solution. "
                "Please contact technical support.",
                None,
            )

    def _format_chat_style(self, body: str, category: str, method: str, quality: str) -> str:
        """Produce a concise, chat-style answer: short intro + 3-6 numbered steps."""
        # Strip excessive whitespace and long lines
        cleaned = re.sub(r"\s+", " ", body).strip()
        # Truncate to a reasonable length
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

    def _kb_first_compose(self, kb_context: str, user_query: str) -> str:
        """Compose a concise solution directly from KB context without external LLMs."""
        # Extract up to 5 actionable lines from KB
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
        return (
            f"Brief diagnosis: Based on our knowledge base, here are focused steps for '{user_query[:60]}':\n"
            f"{numbered}\n"
            f"Notes: Refer to the linked KB articles shown above for full details."
        )

    def _generate_enhanced_solution(self, ticket: str, category: str, method: str) -> Tuple[str, str]:
        """
        Structured fallback pipeline for solution generation:
        1. Knowledge Base
        2. Gemini LLM
        3. Hugging Face
        4. Template-based fallback
        
        Returns: (solution_text, source_method)
        """
        
        # ==================
        # Step 1: Knowledge Base
        # ==================
        kb_solution = self.knowledge_base.get(category)
        if kb_solution:
            logging.info(f"Solution found in Knowledge Base for category: {category}")
            final_solution = self._format_chat_style(kb_solution, category, method, "Knowledge Base")
            return final_solution, "Knowledge Base"

        # If ticket contains appended KB/Web context, prioritize a concise KB-only composition
        if "[Context]" in ticket:
            try:
                _, ctx = ticket.split("[Context]", 1)
                ctx = ctx.strip()
                if ctx:
                    composed = self._kb_first_compose(ctx, ticket.split("\n\n[Context]", 1)[0])
                    return self._format_chat_style(composed, category, method, "KB (retrieved)"), "Knowledge Base (retrieved)"
            except Exception:
                pass
        
        logging.info(f"No KB solution found for {category}, trying Gemini...")
        
        # ==================
        # Step 2: Try Gemini
        # ==================
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            gemini_prompt = (
                f"You are a professional support engineer. Analyze and solve the following ticket.\n\n"
                f"Ticket: {ticket}\n\n"
                f"Category: {category}\n\n"
                f"Provide a concise, actionable solution (3–6 sentences) including:\n"
                f"- brief diagnosis\n- numbered steps\n- any cautions or prerequisites."
            )
            response = genai.GenerativeModel("gemini-1.5-flash").generate_content(gemini_prompt)
            gemini_solution = response.text.strip()
            
            if gemini_solution:
                logging.info(f"Solution generated successfully via Gemini for category: {category}")
                final_solution = self._format_chat_style(gemini_solution, category, "Gemini", "AI (LLM)")
                return final_solution, "Gemini"
        except Exception as e:
            logging.warning(f"Gemini LLM failed for category {category}: {e}")

        # ==================
        # Step 2b: Try OpenAI (if available) for concise, chat-style answer
        # ==================
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                client = OpenAI(api_key=openai_key)
                system_prompt = (
                    "You are a senior VS Code extension support engineer. "
                    "Write a concise answer: 1 short diagnosis + 3-6 numbered steps. "
                    "Prefer steps derived from provided context. Avoid long prose."
                )
                user_prompt = (
                    f"Ticket: {ticket}\nCategory: {category}\n"
                    f"Return only the answer without extra disclaimers."
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=350,
                )
                oi_solution = resp.choices[0].message.content.strip()
                if oi_solution:
                    final_solution = self._format_chat_style(oi_solution, category, "OpenAI", "AI (LLM)")
                    return final_solution, "OpenAI"
        except Exception as e:
            logging.warning(f"OpenAI fallback failed: {e}")
        
        logging.info(f"Gemini failed, trying Hugging Face...")
        
        # ==================
        # Step 3: Fallback to Hugging Face
        # ==================
        try:
            hf_model = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")
            hf_prompt = f"User support ticket: {ticket}\n\nProvide a helpful solution:"
            hf_response = hf_model(hf_prompt, max_new_tokens=200, truncation=True)[0]["generated_text"]
            
            # Clean the Hugging Face output
            hf_solution = clean_hf_response(hf_response)
            
            logging.info(f"Hugging Face solution generated for category {category}:\n{hf_solution}")
            
            final_solution = self._format_chat_style(hf_solution, category, "Hugging Face", "AI (Fallback)")
            return final_solution, "Hugging Face"
        except Exception as e:
            logging.error(f"Hugging Face fallback failed for category {category}: {e}")
        
        logging.info(f"All ML models failed, using template-based fallback for category: {category}")
        
        # ==================
        # Step 4: Template-based Static Fallback
        # ==================
        templates = {
            "login_issue": (
                "It looks like you're experiencing a login issue. "
                "Please try resetting your password using the 'Forgot Password' option. "
                "If the problem persists, clear your browser cache and cookies, then attempt again."
            ),
            "bug_report": (
                "For bug reports, please provide steps to reproduce the issue, "
                "expected vs actual behavior, and any error messages. "
                "Our team will investigate and follow up with you shortly."
            ),
            "feature_request": (
                "Thank you for your feature suggestion! "
                "We appreciate your feedback and will review it for consideration in future updates."
            ),
            "network_error": (
                "Check your internet connection, restart your router, "
                "and try again. If the issue persists, contact IT support for assistance."
            ),
        }
        
        template_solution = templates.get(
            category,
            f"We received your ticket: \"{ticket}\".\n\n"
            f"Here are some recommended next steps:\n"
            f"1. Double-check related settings or configurations.\n"
            f"2. Review our documentation for {category}-related issues.\n"
            f"3. If the issue persists, please escalate to technical support."
        )
        
        final_solution = self._format_chat_style(template_solution, category, "template_fallback", "Structured template")
        return final_solution, "Template"

    # -------- Optional compatibility helpers used by CLI/UI -------
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