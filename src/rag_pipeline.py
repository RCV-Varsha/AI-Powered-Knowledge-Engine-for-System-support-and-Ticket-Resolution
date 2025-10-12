# rag_pipeline_cpu.py

import os
import json
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# --- Config ---
LOCAL_DOCS_FILE = "data/pilot_dataset_augmented.json"
VECTORSTORE_PATH = "vectorstore/db_faiss"
MODEL_NAME = "distilgpt2"  # small, CPU-friendly model

# --- Load documents from local JSON ---
def load_docs_from_local_json(json_path=LOCAL_DOCS_FILE):
    if not os.path.exists(json_path):
        print(f"❌ Local docs file not found: {json_path}")
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs = [Document(page_content=item["ticket_content"]) for item in data if "ticket_content" in item]
    print(f"✅ Loaded {len(docs)} docs from local JSON.")
    return docs

# --- Split documents into chunks ---
def split_documents(docs, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)

# --- Build or load FAISS index ---
def get_vectorstore(chunks, embeddings_model):
    if not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.faiss")):
        vector_store = FAISS.from_documents(chunks, embeddings_model)
        vector_store.save_local(VECTORSTORE_PATH)
        print(f"✅ FAISS vectorstore created and saved at {VECTORSTORE_PATH}")
    else:
        vector_store = FAISS.load_local(VECTORSTORE_PATH, embeddings_model)
        print(f"✅ FAISS vectorstore loaded from {VECTORSTORE_PATH}")
    return vector_store

# --- Build QA pipeline ---
def get_qa_pipeline(model_name=MODEL_NAME):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)  # CPU only
    qa_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256
    )
    return qa_pipeline

# --- Interactive Q&A ---
def ask_questions(vector_store, qa_pipeline):
    print("\n💡 RAG QA system ready. Type 'exit' to quit.")
    while True:
        query = input("\n💬 Ask a question: ")
        if query.lower() == "exit":
            break

        # Retrieve relevant documents
        retrieved_docs = vector_store.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        # Instruction prompt for better accuracy
        prompt = (
            f"You are a helpful assistant. Answer the question using ONLY the context below. "
            f"If the answer is not in the context, respond with 'I don't know'.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        )

        result = qa_pipeline(prompt, max_length=256, do_sample=False)[0]["generated_text"]
        print("\n✨ Answer:")
        print(result.strip())

        print("\n📌 Sources:")
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"  {i}. {doc.page_content[:200]}...")  # first 200 chars

# --- Main ---
if __name__ == "__main__":
    docs = load_docs_from_local_json()
    if not docs:
        exit()

    chunks = split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = get_vectorstore(chunks, embeddings)

    qa_pipeline = get_qa_pipeline()
    ask_questions(vector_store, qa_pipeline)
