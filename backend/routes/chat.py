from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.chains.rag_chain import get_rag_chain, get_rag_chain_streaming
from backend.utils.security import require_user
from typing import Optional
from backend.services.sqlite_client import (
    create_chat_message, 
    get_chat_history, 
    get_user_by_username,
    create_chat_session,
    get_user_sessions,
    update_session_title,
    delete_session
)
import uuid
import json
import asyncio

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

@router.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(require_user)):
    user = await get_user_by_username(current_user["username"])
    user_id = user["id"]
    
    session_id = request.session_id
    
    # Create session if not exists
    if not session_id:
        session_id = str(uuid.uuid4())
        # Use first 30 chars of query as title
        title = request.query[:30] + "..." if len(request.query) > 30 else request.query
        await create_chat_session(session_id, user_id, title)
    
    # Get history
    history = await get_chat_history(session_id)
    formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    chain = get_rag_chain()
    response = chain.invoke({
        "question": request.query,
        "chat_history": formatted_history
    })
    
    # Save interaction
    await create_chat_message(user_id, "user", request.query, session_id)
    await create_chat_message(user_id, "assistant", response["answer"], session_id)
    
    return {"answer": response["answer"], "session_id": session_id}

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
            # Import classifier
            from backend.chains.query_classifier import classify_query
            
            # Classify if query needs RAG
            needs_rag = await asyncio.to_thread(classify_query, request.query)
            
            # Send session_id first
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
            
            full_response = ""
            
            if needs_rag:
                # Use RAG for document-based queries
                from backend.chains.rag_chain import get_rag_chain_streaming
                chain, retriever = get_rag_chain_streaming()
                
                # Get context documents
                docs = await asyncio.to_thread(
                    retriever.invoke,
                    request.query
                )
                
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
                from backend.chains.rag_chain import get_simple_chat_chain
                chain = get_simple_chat_chain()
                
                # Stream the response without RAG overhead
                async for chunk in chain.astream({
                    "question": request.query,
                    "chat_history": formatted_history
                }):
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            
            # Save assistant message
            await create_chat_message(user_id, "assistant", full_response, session_id)
            
            # Send done signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
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
