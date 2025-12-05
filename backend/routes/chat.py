from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.chains.rag_chain import get_rag_chain_streaming
from backend.utils.security import require_user, require_admin
from typing import Optional
import uuid
import json
import asyncio
import logging
from backend.services.sqlite_client import (
    create_chat_message, 
    get_chat_history, 
    get_user_by_username,
    create_chat_session,
    get_user_sessions,
    update_session_title,
    delete_session
)
from backend.services.semantic_cache import get_semantic_cache

# Note: Using vectorstore similarity score instead of LLM classifier for efficiency
# Note: Using semantic cache for instant responses on similar queries
            
# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

# Note: Non-streaming /chat endpoint removed - frontend only uses /chat/stream

@router.get("/chat/sessions")
async def get_sessions(current_user: dict = Depends(require_user)):
    user = await get_user_by_username(current_user["username"])
    return await get_user_sessions(user["id"])

@router.get("/chat/history/{session_id}")
async def get_history(session_id: str, current_user: dict = Depends(require_user)):
    return await get_chat_history(session_id)

class SessionUpdate(BaseModel):
    title: str

@router.put("/chat/sessions/{session_id}")
async def update_session(session_id: str, update: SessionUpdate, current_user: dict = Depends(require_user)):
    await update_session_title(session_id, update.title)
    return {"id": session_id, "title": update.title}

@router.delete("/chat/sessions/{session_id}")
async def delete_session_route(session_id: str, current_user: dict = Depends(require_user)):
    # Check if session belongs to user
    user = await get_user_by_username(current_user["username"])
    sessions = await get_user_sessions(user["id"])
    session_ids = [s["id"] for s in sessions]
    
    if session_id not in session_ids:
        raise HTTPException(status_code=403, detail="Not authorized to delete this session")
    
    await delete_session(session_id)
    return {"status": "deleted", "id": session_id}

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, current_user: dict = Depends(require_user)):
    """Stream chat responses using Server-Sent Events"""
    user = await get_user_by_username(current_user["username"])
    user_id = user["id"]
    
    session_id = request.session_id
    
    # Create session if not exists
    if not session_id:
        session_id = str(uuid.uuid4())
        title = request.query[:30] + "..." if len(request.query) > 30 else request.query
        await create_chat_session(session_id, user_id, title)
    
    # Get history
    history = await get_chat_history(session_id)
    formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    # Save user message
    await create_chat_message(user_id, "user", request.query, session_id)
    
    async def generate():
        try:
            # Get semantic cache
            semantic_cache = get_semantic_cache()
            
            # Check semantic cache first
            cache_result = await asyncio.to_thread(semantic_cache.get, request.query)
            
            if cache_result:
                cached_response, distance = cache_result
                logger.info(f"SEMANTIC CACHE HIT (distance: {distance:.4f})")
                
                # Send session_id first
                yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
                
                # Send cached response as if streaming (for consistent UX)
                # Split into chunks for natural streaming feel
                chunk_size = 20  # characters per chunk
                for i in range(0, len(cached_response), chunk_size):
                    chunk = cached_response[i:i + chunk_size]
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for natural feel
                
                # Save assistant message
                await create_chat_message(user_id, "assistant", cached_response, session_id)
                
                # Send done signal with cache indicator
                yield f"data: {json.dumps({'type': 'done', 'cached': True})}\n\n"
                return
            
            # No cache hit - proceed with normal flow
            logger.info("SEMANTIC CACHE MISS - generating new response")
            
            # Get retriever and chain
            from backend.chains.rag_chain import get_simple_chat_chain
            from backend.chains.retriever_chroma import get_vectorstore
            
            chain, retriever = get_rag_chain_streaming()
            vectorstore = get_vectorstore()
            
            # Retrieve documents with similarity scores
            # Note: Use vectorstore directly, not retriever, for similarity_search_with_score
            docs_with_scores = await asyncio.to_thread(
                vectorstore.similarity_search_with_score,
                request.query,
                k=3
            )
            
            # Determine if RAG is needed based on similarity score
            # ChromaDB with OpenAI embeddings uses L2 distance: lower score = more similar
            # Based on testing with text-embedding-3-small:
            #   - Score < 1.0:  Very relevant documents
            #   - Score 1.0-1.5: Possibly relevant documents  
            #   - Score > 1.5: Not relevant (general conversation)
            needs_rag = False
            similarity_score = float('inf')
            
            if docs_with_scores:
                # Get the best (lowest) distance score
                similarity_score = docs_with_scores[0][1]
                
                # Threshold: 1.5 for L2 distance with OpenAI embeddings
                # Documents within 1.5 distance are considered relevant
                if similarity_score < 1.5:
                    needs_rag = True
            
            # Log classification result with similarity score
            if needs_rag:
                logger.info(f"USED RAG (similarity score: {similarity_score:.4f})")
            else:
                logger.info(f"NOT USED RAG (similarity score: {similarity_score:.4f})")
            
            # Send session_id first
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
            
            full_response = ""
            
            if needs_rag:
                # Use RAG with already-retrieved documents (no second retrieval!)
                docs = [doc for doc, score in docs_with_scores]
                
                # Stream the response with context
                async for chunk in chain.astream({
                    "context": docs,
                    "question": request.query,
                    "chat_history": formatted_history
                }):
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            else:
                # Use simple chat for conversational queries (much faster!)
                simple_chain = get_simple_chat_chain()
                
                # Stream the response without RAG overhead
                async for chunk in simple_chain.astream({
                    "question": request.query,
                    "chat_history": formatted_history
                }):
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            
            # Save assistant message
            await create_chat_message(user_id, "assistant", full_response, session_id)
            
            # Cache the response for future similar queries
            await asyncio.to_thread(semantic_cache.set, request.query, full_response)
            
            # Send done signal
            yield f"data: {json.dumps({'type': 'done', 'cached': False})}\n\n"
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ============== Cache Management Endpoints ==============

@router.get("/cache/stats")
async def get_cache_stats(current_user: dict = Depends(require_admin)):
    """Get semantic cache statistics (admin only)"""
    cache = get_semantic_cache()
    return cache.get_stats()


@router.delete("/cache/clear")
async def clear_cache(current_user: dict = Depends(require_admin)):
    """Clear all semantic cache entries (admin only)"""
    cache = get_semantic_cache()
    cleared_count = await asyncio.to_thread(cache.clear)
    return {
        "status": "success",
        "message": f"Cleared {cleared_count} cache entries"
    }
