import chromadb
from backend.utils.config import settings

def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
