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
import re
import time
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
            start_time = time.time()
            
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
            
            # Check for simple greetings FIRST (no LLM needed)
            from backend.services.query_classifier import is_simple_greeting, get_instant_response
            if is_simple_greeting(request.query):
                response = get_instant_response(request.query)
                
                # Stream instantly
                for word in response.split():
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                
                await create_chat_message(user_id, "assistant", response, session_id)
                total_time = time.time() - start_time
                logger.info(f"INSTANT RESPONSE: {total_time:.2f}s (simple greeting)")
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            # Rewrite query with context (for non-greeting queries)
            t1 = time.time()
            search_query = await rewrite_query_with_context(request.query, formatted_history)
            rewrite_time = time.time() - t1
            logger.info(f"[{rewrite_time:.2f}s] QUERY REWRITING: '{request.query}' -> '{search_query}'")
            
            # Check if query needs RAG retrieval
            t2 = time.time()
            needs_rag = await is_reimbursement_related_async(search_query)
            classify_time = time.time() - t2
            logger.info(f"[{classify_time:.2f}s] CLASSIFICATION: Needs RAG = {needs_rag}")
            
            if not needs_rag:
                # Non-RAG response (longer conversational messages)
                t3 = time.time()
                response = await get_chat_response(request.query)
                chat_time = time.time() - t3
                
                for word in response.split():
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                    await asyncio.sleep(0.02)
                
                await create_chat_message(user_id, "assistant", response, session_id)
                total_time = time.time() - start_time
                logger.info(f"NON-RAG RESPONSE: {total_time:.2f}s (rewrite: {rewrite_time:.2f}s, classify: {classify_time:.2f}s, chat: {chat_time:.2f}s)")
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            # RAG flow 
            chain, retriever = get_rag_chain()
            vectorstore = get_vectorstore()
            
            # Retrieve relevant documents using rewritten query
            t3 = time.time()
            docs_with_scores = await asyncio.to_thread(
                vectorstore.similarity_search_with_score,
                search_query,
                k=10
            )
            retrieval_time = time.time() - t3
            logger.info(f"[{retrieval_time:.2f}s] RETRIEVED {len(docs_with_scores)} DOCUMENTS")
            
            full_response = ""
            docs = [doc for doc, score in docs_with_scores]
            
            t4 = time.time()
            first_token_time = None
            async for chunk in chain.astream({
                "context": docs,
                "question": request.query,
                "chat_history": formatted_history
            }):
                if chunk:
                    if first_token_time is None:
                        first_token_time = time.time() - t4
                        logger.info(f"[{first_token_time:.2f}s] First token received")
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            
            generation_time = time.time() - t4
            
            # Parse citations from response [ref:N] format
            cited_refs = set(map(int, re.findall(r'\[ref:(\d+)\]', full_response)))
            logger.info(f"Cited references: {cited_refs}")
            
            # Clean response by removing citation markers for saved version
            clean_response = re.sub(r'\s*\[ref:\d+\]', '', full_response)
            await create_chat_message(user_id, "assistant", clean_response, session_id)
            
            # Show only sources that were actually cited by the LLM
            if cited_refs and docs_with_scores:
                sources = []
                seen_sources = set()  # Avoid duplicate filenames
                
                for ref_num in sorted(cited_refs):
                    # ref_num is 1-indexed, docs_with_scores is 0-indexed
                    if ref_num <= len(docs_with_scores):
                        doc, score = docs_with_scores[ref_num - 1]
                        source_name = doc.metadata.get("source", "Unknown")
                        
                        # Skip if already shown this source
                        if source_name in seen_sources:
                            continue
                        
                        seen_sources.add(source_name)
                        similarity_pct = 100 * math.exp(-score * 0.5)
                        
                        sources.append({
                            "number": len(sources) + 1,
                            "source": source_name,
                            "similarity": round(similarity_pct, 1)
                        })
                
                if sources:
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            
            total_time = time.time() - start_time
            logger.info(f"RAG RESPONSE: {total_time:.2f}s (rewrite: {rewrite_time:.2f}s, classify: {classify_time:.2f}s, retrieval: {retrieval_time:.2f}s, generation: {generation_time:.2f}s)")
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
