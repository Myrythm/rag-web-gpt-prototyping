import shutil
import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import fitz  # PyMuPDF
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
from backend.chains.retriever_chroma import get_vectorstore
from backend.utils.security import require_admin, get_password_hash
from backend.utils.config import settings
from backend.services.langsmith_client import get_recent_traces
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])


def extract_text_with_tables(doc) -> str:
    """
    Extract text from PDF with better table handling.
    Uses PyMuPDF's table detection to preserve table structure.
    """
    full_text = []
    
    for page_num, page in enumerate(doc):
        page_text_parts = []
        
        # Try to find tables on this page
        try:
            tables = page.find_tables()
            
            if tables.tables:
                # Page has tables - extract them with structure
                for table in tables.tables:
                    table_data = table.extract()
                    
                    if table_data:
                        # Format table as structured text
                        # Each row becomes a clear line with column headers context
                        headers = table_data[0] if table_data else []
                        
                        for row_idx, row in enumerate(table_data):
                            if row_idx == 0:
                                # Header row
                                header_text = " | ".join([str(cell) if cell else "" for cell in row])
                                page_text_parts.append(f"[Table Header]: {header_text}")
                            else:
                                # Data row - pair with headers for context
                                row_parts = []
                                for col_idx, cell in enumerate(row):
                                    if cell:
                                        header = headers[col_idx] if col_idx < len(headers) and headers[col_idx] else f"Column{col_idx+1}"
                                        row_parts.append(f"{header}: {cell}")
                                
                                if row_parts:
                                    page_text_parts.append(" | ".join(row_parts))
                        
                        page_text_parts.append("")  # Empty line after table
                
                # Also get non-table text from the page
                # Get text blocks and filter out those that overlap with tables
                non_table_text = []
                blocks = page.get_text("blocks")
                table_rects = [fitz.Rect(t.bbox) for t in tables.tables]
                
                for block in blocks:
                    if block[6] == 0:  # Text block
                        block_rect = fitz.Rect(block[:4])
                        # Check if this block overlaps with any table
                        is_in_table = any(block_rect.intersects(tr) for tr in table_rects)
                        if not is_in_table:
                            non_table_text.append(block[4].strip())
                
                if non_table_text:
                    page_text_parts.insert(0, "\n".join(non_table_text))
            else:
                # No tables found - use regular text extraction
                page_text_parts.append(page.get_text())
                
        except Exception as e:
            # Fallback to regular text extraction if table detection fails
            page_text_parts.append(page.get_text())
        
        if page_text_parts:
            full_text.append(f"\n--- Page {page_num + 1} ---\n" + "\n".join(page_text_parts))
    
    return "\n\n".join(full_text)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin)
):
    # 1. Read content
    content = await file.read()
    
    # 2. Extract text using PyMuPDF with improved table handling
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text = extract_text_with_tables(doc)
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")
    
    # 3. Chunk
    chunks = chunk_text(text)
    
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
    
    return {"id": doc_id, "filename": file.filename, "chunks": len(chunks)}


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
