from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Step 3: Split documents into chunks
def split_documents(
    docs: list[Document],
    chunk_size: int,
    chunk_overlap: int
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)

# ---- Test the function ----
if __name__ == "__main__":
    # Example document (later you will replace this with Google Sheet or PDF data)
    docs = [Document(page_content="This is a long text. We want to split it into chunks for RAG testing.")]
    
    chunks = split_documents(docs, chunk_size=20, chunk_overlap=5)
    
    print(f"✅ Total Chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}: {chunk.page_content}")
