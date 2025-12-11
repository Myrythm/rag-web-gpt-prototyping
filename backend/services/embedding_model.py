from langchain_openai import OpenAIEmbeddings
from backend.utils.config import settings

def get_embedding_model():
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=settings.OPENAI_API_KEY
    )
