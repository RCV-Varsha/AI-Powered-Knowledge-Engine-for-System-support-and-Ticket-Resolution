# kb_processor.py - HuggingFace Embeddings Version

import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings  # ✅ New import

# --- Config ---
KB_FOLDER = "kb"   # folder where your markdown docs are stored
DB_FAISS_PATH = Path("vectorstore/db_faiss")

def load_markdown_documents():
    """Load only Markdown documents from the knowledge base folder."""
    if not os.path.exists(KB_FOLDER):
        print(f"⚠️ Knowledge base folder '{KB_FOLDER}' not found.")
        return []

    try:
        md_loader = DirectoryLoader(
            KB_FOLDER, 
            glob="**/*.md", 
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        md_docs = md_loader.load()
        print(f"📄 Loaded {len(md_docs)} Markdown files")
        
        for doc in md_docs:
            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                filename = Path(doc.metadata['source']).name
                content_preview = doc.page_content[:100].replace('\n', ' ')
                print(f"  ✓ {filename}: {content_preview}...")

        return md_docs
        
    except Exception as e:
        print(f"❌ Error loading documents: {str(e)}")
        return []

def split_documents(docs):
    """Split documents into chunks for processing."""
    if not docs:
        print("⚠️ No documents to split.")
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

def get_embeddings():
    """Get HuggingFace embeddings (free, no API key needed)."""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"  # ✅ Lightweight & free
        )
        return embeddings
    except Exception as e:
        raise RuntimeError(f"❌ Error initializing HuggingFace embeddings: {e}")

def create_vectorstore(chunks):
    """Create and save FAISS vectorstore from document chunks."""
    if not chunks:
        print("⚠️ No chunks to process.")
        return None
    
    try:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        DB_FAISS_PATH.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(DB_FAISS_PATH))
        print(f"✅ Vectorstore saved at {DB_FAISS_PATH.resolve()}")
        return vectorstore
        
    except Exception as e:
        print(f"❌ Error creating vectorstore: {str(e)}")
        return None

def load_vectorstore():
    """Load existing FAISS vectorstore."""
    if not DB_FAISS_PATH.exists():
        print(f"⚠️ Vectorstore not found at {DB_FAISS_PATH}. Run processing first.")
        return None
    
    try:
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            str(DB_FAISS_PATH),
            embeddings
        )
        print(f"✅ Loaded vectorstore from {DB_FAISS_PATH}")
        return vectorstore
        
    except Exception as e:
        print(f"❌ Error loading vectorstore: {str(e)}")
        return None

class MarkdownProcessor:
    """Class to handle markdown processing and indexing for the knowledge base."""

    def __init__(self, kb_folder=None, db_path=None):
        self.kb_folder = kb_folder or KB_FOLDER
        self.db_path = db_path or DB_FAISS_PATH
    
    def process_and_index_kb(self, rebuild=False):
        """Process and index the knowledge base."""
        if not rebuild and self.db_path.exists():
            print(f"✅ Knowledge base index already exists at {self.db_path}")
            return True
        
        print("🚀 Processing and indexing knowledge base...")
        
        documents = load_markdown_documents()
        if not documents:
            print("⚠️ No markdown files found to process.")
            return False
        
        chunks = split_documents(documents)
        if not chunks:
            print("❌ Failed to create chunks from documents.")
            return False
        
        vectorstore = create_vectorstore(chunks)
        if vectorstore:
            print("🎉 Knowledge base processing completed successfully!")
            print(f"📊 Total documents: {len(documents)}")
            print(f"📊 Total chunks: {len(chunks)}")
            return True
        else:
            print("❌ Failed to create vectorstore.")
            return False

def load_kb_retriever():
    """Load the knowledge base retriever for use in solution generation."""
    try:
        vectorstore = load_vectorstore()
        if vectorstore:
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            print("✅ Knowledge base retriever loaded successfully")
            return retriever
        else:
            print("❌ Failed to load vectorstore for retriever")
            return None
    except Exception as e:
        print(f"❌ Error loading KB retriever: {str(e)}")
        return None

def search_kb(query, k=5):
    """Search the knowledge base for relevant information."""
    try:
        vectorstore = load_vectorstore()
        if not vectorstore:
            return []
        
        results = vectorstore.similarity_search(query, k=k)
        print(f"🔍 Found {len(results)} relevant documents for: '{query}'")
        return results
    except Exception as e:
        print(f"❌ Error searching knowledge base: {str(e)}")
        return []

def test_kb_system():
    """Test the knowledge base system end-to-end"""
    print("🧪 Testing Knowledge Base System")
    print("=" * 50)
    
    processor = MarkdownProcessor()
    success = processor.process_and_index_kb(rebuild=False)
    
    if not success:
        print("❌ KB processing failed")
        return
    
    retriever = load_kb_retriever()
    if not retriever:
        print("❌ Failed to load retriever")
        return
    
    test_query = "VS Code extension"
    results = search_kb(test_query, k=3)
    
    print(f"\n📋 Search Results for '{test_query}':")
    for i, result in enumerate(results, 1):
        content_preview = result.page_content[:200].replace('\n', ' ')
        source = result.metadata.get('source', 'Unknown')
        print(f"{i}. {Path(source).name}: {content_preview}...")
    
    print("\n✅ Knowledge base system test completed!")

def main():
    """Main processing pipeline for Markdown files."""
    print("🚀 Starting Markdown knowledge base processing...")
    
    processor = MarkdownProcessor()
    success = processor.process_and_index_kb(rebuild=True)
    
    if success:
        print("\n🧪 Running system test...")
        test_kb_system()
    else:
        print("❌ Knowledge base processing failed.")

if __name__ == "__main__":
    main()
