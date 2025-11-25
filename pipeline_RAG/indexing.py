import json
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

embedding_model = OllamaEmbeddings(model="embeddinggemma:300m")

script_dir = os.path.dirname(__file__)
chunked_data_path = os.path.join(script_dir, "..", "chunked_data", "chunked_documents.jsonl")
with open(chunked_data_path, "r", encoding="utf-8") as f:
    chunked_documents = [Document(**json.loads(line)["kwargs"]) for line in f]

print("Creating FAISS vector store...")
vector_store = FAISS.from_documents(chunked_documents, embedding_model)

index_path = os.path.join(script_dir, "faiss_index")
vector_store.save_local(index_path)
print(f"FAISS index saved to {index_path}")

vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
# BM25 retriever
bm25_retriever = BM25Retriever.from_documents(chunked_documents)
bm25_retriever.k = 5

# Combine retriever
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)

print("Indexing complete.")

