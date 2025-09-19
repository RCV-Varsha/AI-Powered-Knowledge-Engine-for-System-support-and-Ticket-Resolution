import os
import logging
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from augment_dataset import load_pilot_dataset
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama  # ✅ Ollama import

logging.basicConfig(level=logging.INFO)
load_dotenv()


def get_allowed_categories():
    # Extract unique expected categories from pilot dataset
    dataset_path = os.path.join("data", "pilot_dataset_augmented.json")
    categories = set()
    if os.path.exists(dataset_path):
        with open(dataset_path, encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                categories.add(item["expected_category"].strip().lower())
    return sorted(categories)


class MultiModelResolver:
    def __init__(self, model_name="llama3"):
        logging.info("Initializing MultiModelResolver with Ollama...")

        # Track provider and quota (quota not needed for local models, but kept for compatibility)
        self.llm_provider = "ollama"
        self.quota_exceeded = False

        # Load pilot dataset and categories
        self.pilot_dataset = load_pilot_dataset()
        self.category_list = get_allowed_categories()

        # Use local embeddings for FAISS
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Load FAISS vectorstore
        try:
            self.vectorstore = FAISS.load_local(
                "vectorstore/db_faiss",
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            logging.warning(f"Failed to load FAISS vectorstore: {e}")
            self.vectorstore = None

        # ✅ Initialize Ollama LLM
        self.llm = self._initialize_llm(model_name)

    def _initialize_llm(self, model_name):
        """Initialize Ollama model"""
        try:
            return ChatOllama(
                model=model_name,  # e.g., llama3, mistral, codellama
                temperature=0.1
            )
        except Exception as e:
            logging.error(f"Failed to initialize Ollama LLM: {e}")
            return None

    def categorize_ticket(self, ticket_content):
        """Categorize ticket using LLM first, then fallback to FAISS/template"""
        if self.llm and not self.quota_exceeded:
            try:
                prompt = (
                    f"You are a support AI. Categorize the following ticket by choosing exactly one category from this list (respond ONLY with the category, no extra words):\n"
                    f"{', '.join(self.category_list)}\n"
                    f"Ticket: {ticket_content}"
                )

                # Handle different LLM interfaces
                if hasattr(self.llm, 'invoke'):
                    from langchain_core.messages import HumanMessage
                    completion = self.llm.invoke([HumanMessage(content=prompt)])
                    response = completion.content
                else:
                    completion = self.llm([{"role": "user", "content": prompt}])
                    response = completion.content

                category = response.strip().lower().replace(" ", "_")

                # Map output to closest allowed category (case-insensitive)
                for allowed in self.category_list:
                    if category == allowed:
                        return allowed, self.llm_provider

                # Fallback: fuzzy match
                import difflib
                match = difflib.get_close_matches(category, self.category_list, n=1, cutoff=0.7)
                if match:
                    return match[0], self.llm_provider

                return category, self.llm_provider

            except Exception as e:
                logging.warning(f"{self.llm_provider} error: {e}")

        # Fallback: FAISS similarity search
        if self.vectorstore:
            try:
                results = self.vectorstore.similarity_search(ticket_content, k=1)
                if results and hasattr(results[0], "category"):
                    return results[0].category, "faiss"
            except Exception as e:
                logging.warning(f"FAISS search error: {e}")

        return "uncategorized", "template"

    def generate_solution(self, ticket_content, category, kb_context=""):
        """Generate solution using LLM first, then fallback to template"""
        if self.llm and not self.quota_exceeded:
            try:
                prompt = self._make_solution_prompt(ticket_content, category, kb_context)

                # Handle different LLM interfaces
                if hasattr(self.llm, 'invoke'):
                    from langchain_core.messages import HumanMessage
                    completion = self.llm.invoke([HumanMessage(content=prompt)])
                    solution = completion.content
                else:
                    completion = self.llm([{"role": "user", "content": prompt}])
                    solution = completion.content

                return solution.strip(), self.llm_provider

            except Exception as e:
                logging.warning(f"{self.llm_provider} error (solution): {e}")

        # Fallback: Template solution
        return self._template_solution(ticket_content, category, kb_context), "template"

    def _make_solution_prompt(self, content, category, kb_context):
        """Create solution generation prompt"""
        return f"""You are a VS Code extension support expert. Help with this {category} ticket:

Issue: {content}

{kb_context}

Provide a clear, professional solution with:
1. Problem analysis
2. Step-by-step fix
3. Alternative approaches

Keep response concise and actionable."""

    def _template_solution(self, content, category, kb_context):
        """Generate template-based solution"""
        solution = {
            "bug_report": "Please provide more details about the bug. Restart VS Code and try disabling other extensions.",
            "feature_request": "Thank you for your suggestion! Your feature request has been noted.",
            "performance": "Try disabling unused extensions and restarting VS Code for improved performance.",
            "authentication": "Ensure you are logged in with the correct credentials.",
            "documentation": "Refer to the official documentation for guidance.",
            "technical_issue": "Check your installation and configuration settings.",
            "integration": "Review API documentation and connection settings.",
            "ui_ux": "Try updating the extension or resetting your workspace settings."
        }.get(category, "Thank you for reaching out. Please provide more details about your issue.")

        if kb_context:
            solution += f"\n\n**Knowledge Base Info:**\n{kb_context}"

        solution += f"""

---
**🎯 Professional Support System**
- Category: {category}
- AI-Powered Analysis: Template-based (High reliability)
- Knowledge Base: {"Integrated" if kb_context else "Not available"}
- Response Quality: Production-grade

*This professional solution was generated by our AI-powered support system. For additional assistance, please contact our technical support team.*"""
        return solution

    def safe_categorize_ticket(self, ticket_content):
        """Safe wrapper for categorization with error handling"""
        try:
            return self.categorize_ticket(ticket_content)
        except Exception as e:
            logging.error(f"Categorization error: {e}")
            return "uncategorized", "failed"

    def safe_generate_solution(self, ticket_content, category, kb_context=""):
        """Safe wrapper for solution generation with error handling"""
        try:
            return self.generate_solution(ticket_content, category, kb_context)
        except Exception as e:
            logging.error(f"Solution generation error: {e}")
            return self._template_solution(ticket_content, category, kb_context), "failed"
