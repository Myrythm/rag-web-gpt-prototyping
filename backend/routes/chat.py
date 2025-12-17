from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.chains.rag_chain import get_rag_chain
from backend.utils.security import require_user, require_admin
from typing import Optional
import uuid
import json
import asyncio
import logging
import math
from backend.chains.retriever_chroma import get_vectorstore
from backend.services.query_classifier import is_reimbursement_related_async, get_chat_response
from backend.services.query_rewriter import rewrite_query_with_context
from backend.services.sqlite_client import (
    create_chat_message, 
    get_chat_history, 
    get_user_by_username,
    create_chat_session,
    get_user_sessions,
    update_session_title,
    delete_session
)
            
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


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
    user = await get_user_by_username(current_user["username"])
    sessions = await get_user_sessions(user["id"])
    session_ids = [s["id"] for s in sessions]
    
    if session_id not in session_ids:
        raise HTTPException(status_code=403, detail="Not authorized to delete this session")
    
    await delete_session(session_id)
    return {"status": "deleted", "id": session_id}

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, current_user: dict = Depends(require_user)):
    user = await get_user_by_username(current_user["username"])
    user_id = user["id"]
    
    session_id = request.session_id
    
    if not session_id:
        session_id = str(uuid.uuid4())
        title = request.query[:30] + "..." if len(request.query) > 30 else request.query
        await create_chat_session(session_id, user_id, title)
    
    history = await get_chat_history(session_id)
    formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    await create_chat_message(user_id, "user", request.query, session_id)
    
    async def generate():
        try:
            
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
            
            # Rewrite query with context FIRST (before classification)
            search_query = await rewrite_query_with_context(request.query, formatted_history)
            logger.info(f"Original: '{request.query}' -> Rewritten: '{search_query}'")
            
            # Check if query needs RAG retrieval (using rewritten query for better context)
            needs_rag = await is_reimbursement_related_async(search_query)
            
            if not needs_rag:
                # Simple response without RAG (greetings, thanks, etc.)
                response = await get_chat_response(request.query)
                
                # Stream the response word by word for consistency
                for word in response.split():
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                    await asyncio.sleep(0.02)  # Small delay for natural feel
                
                await create_chat_message(user_id, "assistant", response, session_id)
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            # RAG flow 
            chain, retriever = get_rag_chain()
            vectorstore = get_vectorstore()
            
            # Retrieve relevant documents using rewritten query (search_query from above)
            docs_with_scores = await asyncio.to_thread(
                vectorstore.similarity_search_with_score,
                search_query,
                k=20
            )
            
            full_response = ""
            docs = [doc for doc, score in docs_with_scores]
            
            async for chunk in chain.astream({
                "context": docs,
                "question": request.query,
                "chat_history": formatted_history
            }):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            
            await create_chat_message(user_id, "assistant", full_response, session_id)
            
            # Show sources only for RAG queries (limit to top 3 unique sources for display)
            if docs_with_scores:
                sources = []
                seen_sources = set()  # Avoid duplicate filenames
                
                for i, (doc, score) in enumerate(docs_with_scores):
                    source_name = doc.metadata.get("source", "Unknown")
                    
                    # Skip if already shown this source
                    if source_name in seen_sources:
                        continue
                    
                    similarity_pct = 100 * math.exp(-score * 0.5)
                    
                    if similarity_pct >= 60:
                        seen_sources.add(source_name)
                        sources.append({
                            "number": len(sources) + 1,
                            "source": source_name,
                            "similarity": round(similarity_pct, 1)
                        })
                    
                    #  n-top sources for display
                    if len(sources) == 1:
                        break
                
                if sources:
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
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
