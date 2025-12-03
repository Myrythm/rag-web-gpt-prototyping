from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.chains.rag_chain import get_rag_chain
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
