"""
Provides a search function that the agents can call to get agricultural knowledge.
"""
from pathlib import Path
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

_vectorstore = None

def _get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    persist_dir = settings.CHROMA_PERSIST_DIR
    if not os.path.isabs(persist_dir):
        persist_dir = os.path.join(Path(__file__).parent.parent.parent, persist_dir)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    _vectorstore = Chroma(
        collection_name="agriculture_kb",
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )
    return _vectorstore

def search_kb(query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant agricultural knowledge from the vector store.
    Returns a single string with the combined content.
    """
    try:
        vectorstore = _get_vectorstore()
        if vectorstore._collection.count() == 0:
            # Try to ingest automatically
            from app.rag.ingest import ingest_documents
            ingest_documents()
            vectorstore = _get_vectorstore()

        results = vectorstore.similarity_search(query, k=top_k)
        if not results:
            return "No relevant information found in the knowledge base."

        parts = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "unknown")
            parts.append(f"[{i}] (Source: {source})\n{doc.page_content}")
        return "\n\n".join(parts)
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"