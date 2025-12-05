import chromadb
from chromadb.config import Settings
import hashlib
import time
from typing import Optional, Tuple
from backend.services.embedding_model import get_embedding_model
from backend.utils.config import settings
import logging

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_COLLECTION_NAME = "semantic_cache"
SIMILARITY_THRESHOLD = 0.8  # L2 distance threshold (lower = more similar)
CACHE_TTL_SECONDS = 86400 * 7 # 7 days cache TTL


"""Semantic cache using ChromaDB for vector similarity search"""
class SemanticCache:
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to reuse the cache instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.embedding_model = get_embedding_model()
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY
        )
        
        # Get or create the cache collection
        self.collection = self.client.get_or_create_collection(
            name=CACHE_COLLECTION_NAME,
            metadata={"description": "Semantic cache for LLM responses"}
        )
        
        self._initialized = True
        logger.info(f"Semantic cache initialized with {self.collection.count()} entries")
    
    def _generate_cache_id(self, query: str) -> str:
        """Generate a unique ID for the cache entry"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Tuple[str, float]]:
        """
        Look up a semantically similar query in the cache.
        
        Args:
            query: The user's query
            
        Returns:
            Tuple of (cached_response, similarity_score) if found, None otherwise
        """
        try:
            # Search for similar queries
            results = self.collection.query(
                query_texts=[query],
                n_results=1,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["ids"][0]:
                return None
            
            # Check similarity threshold (L2 distance)
            distance = results["distances"][0][0]
            
            if distance > SIMILARITY_THRESHOLD:
                logger.info(f"Cache miss - distance {distance:.4f} > threshold {SIMILARITY_THRESHOLD}")
                return None
            
            # Check TTL
            metadata = results["metadatas"][0][0]
            cached_time = metadata.get("timestamp", 0)
            
            if time.time() - cached_time > CACHE_TTL_SECONDS:
                logger.info("Cache miss - entry expired")
                # Remove expired entry
                self.collection.delete(ids=[results["ids"][0][0]])
                return None
            
            cached_response = results["documents"][0][0]
            original_query = metadata.get("original_query", "")
            
            logger.info(
                f"CACHE HIT! Distance: {distance:.4f} | "
                f"Original: '{original_query[:50]}...' | "
                f"Current: '{query[:50]}...'"
            )
            
            return (cached_response, distance)
            
        except Exception as e:
            logger.error(f"Cache lookup error: {e}")
            return None
    
    def set(self, query: str, response: str) -> bool:
        """
        Store a query-response pair in the cache.
        
        Args:
            query: The user's query
            response: The LLM's response
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_id = self._generate_cache_id(query)
            
            # Check if this exact query already exists
            existing = self.collection.get(ids=[cache_id])
            
            if existing["ids"]:
                # Update existing entry
                self.collection.update(
                    ids=[cache_id],
                    documents=[response],
                    metadatas=[{
                        "original_query": query,
                        "timestamp": time.time(),
                        "response_length": len(response)
                    }]
                )
            else:
                # Add new entry
                self.collection.add(
                    ids=[cache_id],
                    documents=[response],
                    metadatas=[{
                        "original_query": query,
                        "timestamp": time.time(),
                        "response_length": len(response)
                    }]
                )
            
            logger.info(f"Cached response for query: '{query[:50]}...'")
            return True
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
            return False
    
    """Clear all cache entries. Returns number of entries cleared."""
    def clear(self) -> int:
        try:
            count = self.collection.count()
            self.client.delete_collection(CACHE_COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=CACHE_COLLECTION_NAME,
                metadata={"description": "Semantic cache for LLM responses"}
            )
            logger.info(f"Cleared {count} cache entries")
            return count
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    """Get cache statistics"""
    def get_stats(self) -> dict:
        try:
            count = self.collection.count()
            return {
                "total_entries": count,
                "similarity_threshold": SIMILARITY_THRESHOLD,
                "ttl_seconds": CACHE_TTL_SECONDS,
                "ttl_days": CACHE_TTL_SECONDS / 86400
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}


# Singleton instance
_cache_instance: Optional[SemanticCache] = None


"""Get the singleton semantic cache instance"""
def get_semantic_cache() -> SemanticCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SemanticCache()
    return _cache_instance
