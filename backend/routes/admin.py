import shutil
import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.services.sqlite_client import (
    create_document, 
    get_all_documents, 
    get_documents_paginated,
    get_document_count,
    get_total_chunks,
    delete_document, 
    get_all_users,
    get_users_paginated,
    get_user_count,
    get_user_by_username,
    create_user,
    update_user,
    delete_user
)
from backend.services.chunker import chunk_text
from backend.services.file_converter import convert_to_markdown, get_supported_extensions
from backend.chains.retriever_chroma import get_vectorstore
from backend.utils.security import require_admin, get_password_hash
from backend.utils.config import settings
from backend.services.langsmith_client import get_recent_traces
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(require_admin)
):
    supported = get_supported_extensions()
    results = []
    errors = []
    
    for file in files:
        try:
            # Check file extension
            ext = file.filename.lower().split(".")[-1]
            if ext not in supported:
                raise ValueError(f"Unsupported file type: {ext}. Supported: {', '.join(supported)}")
            
            # 1. Read content
            content = await file.read()
            
            # 2. Convert to Markdown (universal converter)
            markdown_text = convert_to_markdown(content, file.filename)
            
            # 3. Chunk using Markdown-aware splitter
            chunks = chunk_text(markdown_text)
            
            # 4. ID generation
            doc_id = str(uuid.uuid4())
            
            # 5. Add to Chroma
            vectorstore = get_vectorstore()
            # Add metadata to allow deletion by doc_id
            metadatas = [{"document_id": doc_id, "source": file.filename} for _ in chunks]
            vectorstore.add_texts(texts=chunks, metadatas=metadatas)
            
            # 6. Save to SQLite
            doc_data = {
                "id": doc_id,
                "filename": file.filename,
                "chunk_count": len(chunks)
            }
            await create_document(doc_data)
            
            results.append({
                "id": doc_id, 
                "filename": file.filename, 
                "chunks": len(chunks),
                "status": "success"
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e),
                "status": "failed"
            })
    
    return {
        "uploaded": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@router.get("/documents")
async def list_documents(
    page: int = 1, 
    limit: int = 20, 
    search: str = None,
    current_user: dict = Depends(require_admin)
):
    offset = (page - 1) * limit
    docs = await get_documents_paginated(limit, offset, search)
    total = await get_document_count(search)
    return {
        "items": docs,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.delete("/documents/{doc_id}")
async def delete_doc(doc_id: str, current_user: dict = Depends(require_admin)):
    # Delete from SQLite
    await delete_document(doc_id)
    
    # Delete from Chroma
    vectorstore = get_vectorstore()
    # Accessing the underlying collection to delete by metadata
    try:
        vectorstore._collection.delete(where={"document_id": doc_id})
    except Exception as e:
        # Log error but don't fail if already deleted or issue with Chroma
        print(f"Error deleting from Chroma: {e}")
    
    return {"status": "deleted", "id": doc_id}


class BulkDeleteRequest(BaseModel):
    document_ids: list[str]


@router.post("/documents/bulk-delete")
async def bulk_delete_docs(request: BulkDeleteRequest, current_user: dict = Depends(require_admin)):
    """Delete multiple documents at once."""
    deleted = []
    errors = []
    
    vectorstore = get_vectorstore()
    
    for doc_id in request.document_ids:
        try:
            # Delete from SQLite
            await delete_document(doc_id)
            
            # Delete from Chroma
            try:
                vectorstore._collection.delete(where={"document_id": doc_id})
            except Exception as e:
                print(f"Error deleting {doc_id} from Chroma: {e}")
            
            deleted.append(doc_id)
        except Exception as e:
            errors.append({"id": doc_id, "error": str(e)})
    
    return {
        "deleted_count": len(deleted),
        "deleted": deleted,
        "errors": errors
    }


@router.get("/stats")
async def get_stats(current_user: dict = Depends(require_admin)):
    doc_count = await get_document_count()
    total_chunks = await get_total_chunks()
    user_count = await get_user_count()
    return {
        "total_documents": doc_count,
        "total_chunks": total_chunks,
        "total_users": user_count,
        "recent_traces": []
    }


@router.get("/users")
async def list_users_route(
    page: int = 1, 
    limit: int = 20, 
    search: str = None,
    role: str = None,
    current_user: dict = Depends(require_admin)
):
    offset = (page - 1) * limit
    users = await get_users_paginated(limit, offset, search, role)
    total = await get_user_count(search, role)
    return {
        "items": users,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    username: str
    role: str
    password: str = None


@router.post("/users")
async def create_new_user(user: UserCreate, current_user: dict = Depends(require_admin)):
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    user_data = {
        "id": user_id,
        "username": user.username,
        "password_hash": hashed_password,
        "role": user.role
    }
    await create_user(user_data)
    return {"id": user_id, "username": user.username, "role": user.role}


@router.put("/users/{user_id}")
async def update_user_route(user_id: str, user: UserUpdate, current_user: dict = Depends(require_admin)):
    # Check if username is already taken by another user
    existing_user = await get_user_by_username(user.username)
    if existing_user and existing_user["id"] != user_id:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    password_hash = None
    if user.password:
        password_hash = get_password_hash(user.password)
    
    await update_user(user_id, user.username, user.role, password_hash)
    return {"id": user_id, "username": user.username, "role": user.role}


@router.delete("/users/{user_id}")
async def delete_user_route(user_id: str, current_user: dict = Depends(require_admin)):
    # Prevent deleting yourself
    user = await get_user_by_username(current_user["username"])
    if user["id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    await delete_user(user_id)
    return {"status": "deleted", "id": user_id}
