from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
import json
import os

def chunk_documents():
    header_split = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    md_splitter = MarkdownHeaderTextSplitter(header_split)

    metadata_map = {}
    filename_to_id_map = {}
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, "..", "data_khoa_hoc_bkacad")

    with open(os.path.join(data_dir, "metadata.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            metadata = json.loads(line)
            if "id" in metadata and "filename" in metadata:
                metadata_map[metadata["id"]] = metadata
                filename_to_id_map[metadata["filename"]] = metadata["id"]

    chunked_documents = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(data_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            chunks = md_splitter.split_text(content)
            
            if filename in filename_to_id_map:
                doc_id = filename_to_id_map[filename]
                if doc_id in metadata_map:
                    base_metadata = metadata_map[doc_id]
                    for chunk in chunks:
                        chunk.metadata.update(base_metadata)
                        chunked_documents.append(chunk)

    output_folder = os.path.join(script_dir, "..", "chunked_data")
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "chunked_documents.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in chunked_documents:
            doc_dict = {"page_content": doc.page_content, "metadata": doc.metadata}
            f.write(json.dumps(doc_dict, ensure_ascii=False) + "\n")
    
    print(f"Successfully chunked {len(chunked_documents)} documents and saved to {output_file}")

if __name__ == "__main__":
    chunk_documents()
