import json
import os
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_qdrant import QdrantVectorStore


def load_chunked_documents(chunked_data_path: str) -> list[Document]:
    if not os.path.exists(chunked_data_path):
        raise FileNotFoundError(f"File not found: {chunked_data_path}")

    chunked_documents = []
    with open(chunked_data_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                if "kwargs" in data:
                    chunked_documents.append(Document(**data["kwargs"]))
                elif "page_content" in data:
                    chunked_documents.append(
                        Document(
                            page_content=data["page_content"],
                            metadata=data.get("metadata", {}),
                        )
                    )
                else:
                    print("Warning: Unknown chunk format, skipping line")
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {e}")
            except Exception as e:
                print(f"Error creating Document: {e}")

    if not chunked_documents:
        raise ValueError("No documents loaded from chunked_documents.jsonl")

    print(f"Loaded {len(chunked_documents)} documents")
    return chunked_documents


def main():
    embedding_model = OllamaEmbeddings(model="embeddinggemma:300m")

    script_dir = os.path.dirname(__file__)
    chunked_data_path = os.path.join(
        script_dir, "..", "chunked_data", "chunked_documents.jsonl"
    )
    chunked_documents = load_chunked_documents(chunked_data_path)

    collection_name = "bkacad_chunks"

    print(f"Upserting {len(chunked_documents)} chunks into Qdrant...")
    vector_store = QdrantVectorStore.from_documents(
        documents=chunked_documents,
        embedding=embedding_model,
        url="http://localhost:6333",
        collection_name=collection_name,
    )
    print(f"Qdrant collection `{collection_name}` updated")

    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    bm25_retriever = BM25Retriever.from_documents(chunked_documents)
    bm25_retriever.k = 5

    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.5, 0.5],
    )

    print("Indexing complete.")


if __name__ == "__main__":
    main()