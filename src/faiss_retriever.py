# faiss_retriever.py
"""
FAISS retriever for rich KB content
- Loads Markdown KB files
- Splits into chunks
- Creates/loads FAISS vectorstore
- Returns a retriever object
"""

import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------
# Config
# -----------------------------
KB_FOLDER = "kb"  # Markdown knowledge base folder
DB_FAISS_PATH = Path("vectorstore/db_faiss")  # Local FAISS index folder
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# -----------------------------
# Load Markdown documents
# -----------------------------
def load_markdown_docs(kb_folder=KB_FOLDER):
    if not os.path.exists(kb_folder):
        print(f"⚠️ KB folder '{kb_folder}' not found")
        return []

    loader = DirectoryLoader(
        kb_folder,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} Markdown files")
    return docs

# -----------------------------
# Split documents into chunks
# -----------------------------
def split_docs(docs, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Split {len(docs)} documents into {len(chunks)} chunks")
    return chunks

# -----------------------------
# Embeddings & vectorstore
# -----------------------------
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def create_vectorstore(chunks):
    if not chunks:
        print("⚠️ No chunks to index")
        return None

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    DB_FAISS_PATH.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(DB_FAISS_PATH))
    print(f"✅ Vectorstore saved at {DB_FAISS_PATH.resolve()}")
    return vectorstore

def load_vectorstore():
    if not DB_FAISS_PATH.exists():
        print(f"⚠️ Vectorstore not found at {DB_FAISS_PATH}")
        return None
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(str(DB_FAISS_PATH), embeddings, allow_dangerous_deserialization=True)
    print(f"✅ Loaded vectorstore from {DB_FAISS_PATH}")
    return vectorstore

# -----------------------------
# Get FAISS retriever
# -----------------------------
def get_faiss_retriever(k=5, rebuild=False):
    if rebuild or not DB_FAISS_PATH.exists():
        docs = load_markdown_docs()
        if not docs:
            return None
        chunks = split_docs(docs)
        create_vectorstore(chunks)

    vectorstore = load_vectorstore()
    if not vectorstore:
        print("❌ Failed to load vectorstore")
        return None

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})
    print("✅ FAISS retriever ready")
    return retriever

# -----------------------------
# Quick test
# -----------------------------
if __name__ == "__main__":
    retriever = get_faiss_retriever(rebuild=True)
    if retriever:
        query = "How to change VS Code theme?"
        results = retriever.get_relevant_documents(query)
        for i, doc in enumerate(results, 1):
            src = doc.metadata.get("source", "Unknown")
            print(f"{i}. {Path(src).name}: {doc.page_content[:150]}...")
