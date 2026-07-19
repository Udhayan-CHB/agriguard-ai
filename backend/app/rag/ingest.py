"""
Ingestion script that loads all .txt files from data/documents/ into ChromaDB.
Run once (or automatically on startup if no collection exists).
"""
import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

def ingest_documents():
    # Ensure persist directory exists
    persist_dir = settings.CHROMA_PERSIST_DIR
    if not os.path.isabs(persist_dir):
        persist_dir = os.path.join(Path(__file__).parent.parent.parent, persist_dir)
    os.makedirs(persist_dir, exist_ok=True)

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    # Initialize ChromaDB
    vectorstore = Chroma(
        collection_name="agriculture_kb",
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    # If already populated, skip
    if vectorstore._collection.count() > 0:
        print(f"  ✅ Vector store already has {vectorstore._collection.count()} documents.")
        return vectorstore

    # Load documents from data/documents/
    docs_path = Path(__file__).parent.parent.parent / "data" / "documents"
    if not docs_path.exists():
        print("  ⚠️  No documents directory found. Creating sample documents...")
        docs_path.mkdir(parents=True, exist_ok=True)
        # Create a small sample if needed
        with open(docs_path / "sample.txt", "w", encoding="utf-8") as f:
            f.write("Agriculture is the backbone of many economies.")

    documents = []
    for txt_file in docs_path.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Split into chunks of 500 chars with overlap (simple approach)
        chunk_size = 500
        overlap = 50
        for i in range(0, len(content), chunk_size - overlap):
            chunk = content[i:i+chunk_size]
            if chunk.strip():
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": txt_file.name}
                    )
                )

    if documents:
        vectorstore.add_documents(documents)
        print(f"  ✅ Ingested {len(documents)} chunks from {len(list(docs_path.glob('*.txt')))} files.")
    else:
        print("  ⚠️  No documents found to ingest.")

    return vectorstore