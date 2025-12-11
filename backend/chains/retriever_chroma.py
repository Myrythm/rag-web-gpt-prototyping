from langchain_chroma import Chroma
from backend.services.embedding_model import get_embedding_model
from backend.utils.config import settings

def get_vectorstore():
    embedding_function = get_embedding_model()
    return Chroma(
        collection_name="rag_collection",
        embedding_function=embedding_function,
        persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
        collection_metadata={"hnsw:space": "cosine"}  # Cosine similarity
    )

def get_retriever():
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": 5})
