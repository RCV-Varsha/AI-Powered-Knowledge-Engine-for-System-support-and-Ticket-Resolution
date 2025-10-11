import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# --- Config ---
KB_FOLDER = "kb"   # Folder where your markdown docs are stored
DB_FAISS_PATH = Path("vectorstore/db_faiss")

# -----------------------------
# Document loading & splitting
# -----------------------------
def load_markdown_documents():
    if not os.path.exists(KB_FOLDER):
        print(f"⚠️ KB folder '{KB_FOLDER}' not found")
        return []

    try:
        loader = DirectoryLoader(
            KB_FOLDER,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        docs = loader.load()
        print(f"📄 Loaded {len(docs)} Markdown files")
        for doc in docs:
            filename = Path(doc.metadata.get('source', 'Unknown')).name
            print(f"  ✓ {filename}: {doc.page_content[:100].replace(chr(10), ' ')}...")
        return docs
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return []

def split_documents(docs):
    if not docs:
        print("⚠️ No documents to split")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Split {len(docs)} documents into {len(chunks)} chunks")
    return chunks

# -----------------------------
# Embeddings & Vectorstore
# -----------------------------
def get_embeddings():
    try:
        emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return emb
    except Exception as e:
        raise RuntimeError(f"❌ Error initializing embeddings: {e}")

def create_vectorstore(chunks):
    if not chunks:
        print("⚠️ No chunks to index")
        return None

    try:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        DB_FAISS_PATH.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(DB_FAISS_PATH))
        print(f"✅ Vectorstore saved at {DB_FAISS_PATH.resolve()}")
        return vectorstore
    except Exception as e:
        print(f"❌ Error creating vectorstore: {e}")
        return None


def load_vectorstore():
    if not DB_FAISS_PATH.exists():
        print(f"⚠️ Vectorstore not found at {DB_FAISS_PATH}")
        return None
    try:
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            str(DB_FAISS_PATH),
            embeddings,
            allow_dangerous_deserialization=True  # ✅ Trust your local vectorstore
        )
        print(f"✅ Loaded vectorstore from {DB_FAISS_PATH}")
        return vectorstore
    except Exception as e:
        print(f"❌ Error loading vectorstore: {e}")
        return None

# -----------------------------
# KB Processor Class
# -----------------------------
class MarkdownProcessor:
    def __init__(self, kb_folder=None, db_path=None):
        self.kb_folder = kb_folder or KB_FOLDER
        self.db_path = db_path or DB_FAISS_PATH

    def process_and_index_kb(self, rebuild=False):
        if not rebuild and self.db_path.exists():
            print(f"✅ KB index already exists at {self.db_path}")
            return True

        print("🚀 Processing and indexing KB...")
        docs = load_markdown_documents()
        if not docs:
            return False

        chunks = split_documents(docs)
        if not chunks:
            return False

        vectorstore = create_vectorstore(chunks)
        return vectorstore is not None

# -----------------------------
# KB Retriever / Search
# -----------------------------
def load_kb_retriever():
    vectorstore = load_vectorstore()
    if vectorstore:
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":5})
        print("✅ KB retriever loaded")
        return retriever
    else:
        print("❌ Failed to load KB retriever")
        return None

def search_kb(query, k=5):
    vectorstore = load_vectorstore()
    if not vectorstore:
        print("⚠️ No vectorstore loaded")
        return []

    results = vectorstore.similarity_search(query, k=k)
    print(f"🔍 Found {len(results)} results for query: '{query}'")
    for i, r in enumerate(results, 1):
        src = r.metadata.get("source", "Unknown")
        print(f"{i}. {Path(src).name}: {r.page_content[:100].replace(chr(10), ' ')}...")
    return results

# -----------------------------
# Test KB End-to-End
# -----------------------------
def test_kb_system():
    processor = MarkdownProcessor()
    if not processor.process_and_index_kb(rebuild=True):
        print("❌ KB processing failed")
        return

    retriever = load_kb_retriever()
    if not retriever:
        return

    test_query = "VS Code extension"
    results = search_kb(test_query, k=3)
    print("\n✅ KB system test completed!")

# -----------------------------
# Main Entry
# -----------------------------
if __name__ == "__main__":
    test_kb_system()
