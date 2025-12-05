from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import auth, admin, chat
from backend.services.sqlite_client import init_db
from backend.services.langsmith_client import setup_langsmith
from backend.utils.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    setup_langsmith()
    await init_db()
    
    # Initialize Semantic Cache
    # Note: Using semantic cache instead of LangChain's SQLiteCache
    # because SQLiteCache doesn't work with streaming responses
    try:
        from backend.services.semantic_cache import get_semantic_cache
        cache = get_semantic_cache()
        stats = cache.get_stats()
        print(f"Semantic Cache initialized: {stats['total_entries']} entries cached")
    except Exception as e:
        print(f"Failed to initialize Semantic Cache: {e}")


app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth")
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "RAG Web API is running"}
