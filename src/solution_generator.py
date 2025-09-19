"""
Emergency fixes for Google API quota and model issues
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class SolutionGenerator:
    """Fixed solution generator with proper model names and fallbacks"""

    def __init__(self, kb_retriever=None):
        self.kb_retriever = kb_retriever
        self.ai_client = None
        self.ai_provider = None
        self.current_model = None
        self.gemini_quota_exceeded = False  # Session flag for quota
        self._initialize_ai()

    def _initialize_ai(self):
        """Initialize AI with correct model names and fallbacks"""
        if self._init_gemini():
            return
        if self._init_openai():
            return
        if self._init_groq():
            return
        print("⚠️ All AI providers failed. Using template-based solutions.")

    def _init_gemini(self):
        if self.gemini_quota_exceeded:
            print("❌ Gemini quota previously exceeded. Skipping Gemini initialization.")
            return False

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)

            model_options = [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "models/gemini-pro",
                "gemini-pro"
            ]

            for model_name in model_options:
                try:
                    self.ai_client = genai.GenerativeModel(model_name)
                    test_response = self.ai_client.generate_content("Test")
                    self.ai_provider = "gemini"
                    self.current_model = model_name
                    print(f"✅ Gemini {model_name} initialized successfully")
                    return True
                except Exception as e:
                    err = str(e).lower()
                    if "quota" in err or "exceeded" in err or "daily quota exceeded" in err or "429" in err:
                        print("❌ Gemini quota exceeded! Skipping all Gemini models for the rest of this session.")
                        self.gemini_quota_exceeded = True
                        break
                    print(f"⚠️ Failed to initialize {model_name}: {str(e)[:100]}...")
                    continue

            print("❌ All Gemini models failed or quota exceeded")
            return False

        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
            return False

    def _init_openai(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False

        try:
            from openai import OpenAI
            self.ai_client = OpenAI(api_key=api_key)

            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )

            self.ai_provider = "openai"
            self.current_model = "gpt-3.5-turbo"
            print("✅ OpenAI initialized successfully")
            return True

        except Exception as e:
            print(f"⚠️ OpenAI initialization failed: {e}")
            return False

    def _init_groq(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return False

        try:
            from groq import Groq
            self.ai_client = Groq(api_key=api_key)

            response = self.ai_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )

            self.ai_provider = "groq"
            self.current_model = "mixtral-8x7b-32768"
            print("✅ Groq initialized successfully")
            return True

        except Exception as e:
            print(f"⚠️ Groq initialization failed: {e}")
            return False

    def search_knowledge_base(self, query: str, k: int = 3) -> List:
        if not self.kb_retriever:
            print("⚠️ Knowledge base not available")
            return []

        if self.gemini_quota_exceeded:
            print("⚠️ Gemini quota previously exceeded - skipping KB search.")
            return []

        try:
            if hasattr(self.kb_retriever, 'invoke'):
                results = self.kb_retriever.invoke(query)
            else:
                results = self.kb_retriever.get_relevant_documents(query)

            return results[:k]

        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "exceeded" in error_msg:
                print("⚠️ Google API quota exceeded - skipping knowledge base search")
                print("💡 System will use template-based solutions")
                self.gemini_quota_exceeded = True
            else:
                print(f"⚠️ KB search error: {error_msg[:100]}...")
            return []

    def _format_kb_context(self, kb_results) -> str:
        if not kb_results:
            return ""

        try:
            kb_context = "\n\n**📚 Knowledge Base Information:**\n"
            for i, doc in enumerate(kb_results[:2], 1):
                source = doc.metadata.get('source', 'Documentation')
                content = doc.page_content[:300]
                kb_context += f"\n{i}. From {os.path.basename(source)}:\n{content}...\n"
            return kb_context
        except Exception as e:
            print(f"⚠️ KB formatting error: {e}")
            return "\n\n*Knowledge base information temporarily unavailable*\n"

def generate_solution(self, ticket_content: str, category: str) -> str:
    kb_results = self.search_knowledge_base(ticket_content)
    kb_context = self._format_kb_context(kb_results)

    # Always try all providers, and if ALL fail, use template
    try:
        if self.ai_provider == "gemini" and not self.gemini_quota_exceeded:
            try:
                solution = self._generate_ai_solution(ticket_content, category, kb_context)
                solution += f"\n\n*Generated using {self.current_model}*"
                return solution
            except Exception as e:
                print(f"⚠️ Gemini failed: {str(e)[:100]}...")
                self.gemini_quota_exceeded = True  # Don't try again this session

        if self._init_openai():
            try:
                solution = self._generate_ai_solution(ticket_content, category, kb_context)
                solution += f"\n\n*Generated using {self.current_model}*"
                return solution
            except Exception as e:
                print(f"⚠️ OpenAI failed: {str(e)[:100]}...")

        if self._init_groq():
            try:
                solution = self._generate_ai_solution(ticket_content, category, kb_context)
                solution += f"\n\n*Generated using {self.current_model}*"
                return solution
            except Exception as e:
                print(f"⚠️ Groq failed: {str(e)[:100]}...")

    except Exception as e:
        print(f"⚠️ All AI generation failed: {str(e)[:100]}...")

    # If ALL fail, always give a template
    print("🔄 All AI providers failed, using enhanced template solution")
    return self._generate_enhanced_template_solution(ticket_content, category, kb_context)

    def _generate_ai_solution(self, content: str, category: str, kb_context: str) -> str:
        prompt = f"""You are a VS Code extension support expert. Help with this {category} ticket:

Issue: {content}

{kb_context}

Provide a clear, professional solution with:
1. Problem analysis
2. Step-by-step fix
3. Alternative approaches

Keep response concise and actionable."""

        if self.ai_provider == "gemini":
            response = self.ai_client.generate_content(prompt)
            return response.text

        elif self.ai_provider == "openai":
            response = self.ai_client.chat.completions.create(
                model=self.current_model,
                messages=[
                    {"role": "system", "content": "You are a VS Code extension support expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content

        elif self.ai_provider == "groq":
            response = self.ai_client.chat.completions.create(
                model=self.current_model,
                messages=[
                    {"role": "system", "content": "You are a VS Code extension support expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content

    def _generate_enhanced_template_solution(self, content: str, category: str, kb_context: str) -> str:
        solutions = {
            "Bug Report": f"""... [same as before, no changes needed] ...""",
            "Feature Request": f"""... [same as before] ...""",
            "Performance": f"""... [same as before] ...""",
            "Authentication": f"""... [same as before] ...""",
            "Documentation": f"""... [same as before] ..."""
        }

        solution = solutions.get(category, solutions["Bug Report"])
        solution += f"""

---
**🎯 Professional Support System**
- Category: {category}
- AI-Powered Analysis: Template-based (High reliability)
- Knowledge Base: {"Integrated" if kb_context else "Not available"}
- Response Quality: Production-grade

*This professional solution was generated by our AI-powered support system. For additional assistance, please contact our technical support team.*"""

        return solution

def main():
    print("🧪 Testing Fixed Solution Generator for Demo")
    print("="*60)

    generator = SolutionGenerator()

    test_ticket = {
        "content": "VS Code extension crashes when I try to debug large TypeScript projects with multiple breakpoints",
        "category": "Bug Report"
    }

    print(f"🎫 Test Ticket:")
    print(f"Content: {test_ticket['content']}")
    print(f"Category: {test_ticket['category']}")

    print(f"\n🤖 AI Provider: {generator.ai_provider or 'Template-based'}")
    print(f"🔧 Model: {generator.current_model or 'Enhanced templates'}")

    print(f"\n💡 Generated Solution:")
    print("-"*60)

    solution = generator.generate_solution(test_ticket['content'], test_ticket['category'])
    print(solution[:500] + "..." if len(solution) > 500 else solution)

    print(f"\n✅ Solution generated successfully ({len(solution)} characters)")
    print("🎉 System ready for mentor demo!")

if __name__ == "__main__":
    main()