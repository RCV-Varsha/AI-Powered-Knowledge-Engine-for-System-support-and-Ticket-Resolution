[RAG: Retrieval Augmented Generation]

why RAG?
- LLM rely only on training data (knowledge cutoff)
- Hallucinations: Confident but wrong answers

Solution: RAG
-Benefit: Up to data,accurate,domain-specific answers.
-Visual- Compare LLM-only vs RAG pipeline


RAG-"LLM WITH A LIBRARY+INTENET"

LLM ONLY                VS                  RAG
Pre-trained data                    Extrnal+live data
May hallucinate                     Higher accuracy
Limited(knowledge cutoff)           Always up to date
General                             Domain adaption

RAG Architecture

Retriever: -> Find relevant documents(Product Document)
Augmenter: ->Inject into Prompt
Generator (LLM): ->Produces Final answer

Workflow:
(Query: (hey i have issue with my iphone 14 with battery what should i do?))
                                        |
(Retrieve: It will retrieve best probable/answerable chunks to answer)
                                        |
(Augmented: LLM will answer based on the relevant chunks)

Corpus: Dataset

Retrieval: Find the best chunk out of the (Dataset to answer)
-Sparse Retrieval : TF-IDF , BM25
TF(Term Frequency):This measures how freq a term appears in a doc, A higher term freq suggests the term is more relevant to the document contents
IDF(Inverse Document Frequency): This measures how unique and rare a term is across the entire corpus. Terms that appear in many docs have low IDF, which rare terms have high IDF


                                            |
                            (It's improvement of TF-IDF)
BM25 (ENCODER):Ranking function used by search engines to estimate the relevance of documents to give a search query.

Dense Retrieval:Embedding vector + Similarity search

[This is an apple] -> (GoogleEmbedding) ->[0.565,56.45453,569.60,]

Semantic search :(it searches for the meaning of the word)

This fav an apple
This is fav a car -> (my favourite food is)-> (semantic search)-> your fav food is apple
This is fav cloth


Hybrid Retrieval: Dense+BM25


Place to store these
Vector Databases: [0.565,56.45453. 569.60]
Store in vector DB's
Local: FAISS (pip install faiss-cpu)
Other Vecotr DB's: Pinecone, ChromaDB, Weavite, Milvus

RAG Piplines:
- Ingest DOCS (pdf, website, knowledge base)

Corpus

[ The Digitalocean Cloud Controller Manager lets you provision Digitalocean Load Balancers. To configure advanced settings for the load balancer, add the settings under annotations in the metadata stanza in your service configuration file. To prevent misconfiguration, an invalid value for an annotation results in an error when you apply the config file.

Additional configuration examples are available in the Digitalocean Cloud Controller Manager repository. ]


-Chunk text into passage

[The Digitalocean Cloud Controller Manager lets you provision DigitalOcean Load Balancers.] chunk 1
[ To configure advanced settings for the load balancer, add the settings under annotations in the metadata stanza in your service configuration file]: chunk 2
[To prevent misconfiguration, an invalid value for an annotation results in an error when you apply the config file.]: chunk 3 

-Create Embedding and store in vector DB 
[0.434,340,45343,4353, 353423,4245] 
[343423, 3432432, 34234, 223432,4232]
[443243, 34343,22,32,232,2,45]


-Retrieve top-k docs for query
top-k: Most compatible chunk based on the query (top-k=3)

-Augment query with docs

-Generate final answer


#Installing dependencies
pip install -U/langchain langchain-community langchain-google-genai langchain-text-splitters faiss-cpu pypdf-dotenv


#Set your Google API Key
GOOGLE_API_KEY=''

<!-- #Build the index(from a folder or a single file)
python rag_fass_gemini.py --docs ./my_docs --index-path ./faiss_index --rebuild -->

#Import
#Langchain core + utilities
from langchain_core.document import Document
from langchain_core.prompts import ChatPromptTemplate

#Text Splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Loader for file
from langchain_community.document_loaders import TextLoader,PyPDFLoader

#Faiss vector store
from langchain_community.vectorstores import FAISS

#Google Generative AI(Gemini)
from langchain_google_genai import GoogleGenerativeAiEmbeddings
from langchain_groq import ChatGroq

#RAG chain Builders
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chain import create_retrieval_chain

#.env
#