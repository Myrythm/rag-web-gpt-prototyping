import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "rag-web-prototyping"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "NGAPAIN-YAK"  
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    OPENAI_API_KEY: str
    
    # LangSmith / LangChain
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "rag-web"

    # Paths
    CHROMA_PERSIST_DIRECTORY: str = "./chroma"
    SQLITE_DB_PATH: str = "./rag_web.db"
    LLM_CACHE_PATH: str = ".langchain.db"

    class Config:
        env_file = ".env"

settings = Settings()
