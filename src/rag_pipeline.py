
import os
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
import json


# --- Config ---
LOCAL_DOCS_FILE = "data/pilot_dataset_augmented.json"  # Use your local JSON file


def load_docs_from_local_json(json_path=LOCAL_DOCS_FILE):
    if not os.path.exists(json_path):
        print(f"❌ Local docs file not found: {json_path}")
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs = [Document(page_content=item["ticket_content"]) for item in data if "ticket_content" in item]
    print(f"✅ Loaded {len(docs)} docs from local JSON.")
    return docs

def split_documents(docs, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)


# --- Quick Test ---
if __name__ == "__main__":
    # Step 1: Load docs from local JSON
    docs = load_docs_from_local_json()

    # Step 2: Split docs into chunks
    chunks = split_documents(docs)


    # Step 3: Build or load FAISS index with HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if not os.path.exists("vectorstore/db_faiss/index.faiss"):
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local("vectorstore/db_faiss")
    else:
        vector_store = FAISS.load_local("vectorstore/db_faiss", embeddings)

    # Step 4: Use a local Hugging Face model for Q&A
    qa_pipeline = pipeline("text-generation", model="distilgpt2", device=-1)

    # Step 5: Ask questions interactively
    while True:
        query = input("\n💬 Ask a question (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        # Retrieve relevant docs
        retrieved_docs = vector_store.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
        result = qa_pipeline(prompt, max_length=256, do_sample=False)[0]["generated_text"]

        print("\n✨ Answer:")
        print(result)

        print("\n📌 Sources:")
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"  {i}. {doc.page_content[:200]}...")
