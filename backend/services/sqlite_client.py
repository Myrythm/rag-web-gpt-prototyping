import aiosqlite
from backend.utils.config import settings

DB_PATH = settings.SQLITE_DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable WAL mode for better concurrency
        await db.execute("PRAGMA journal_mode=WAL")
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                chunk_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        await db.commit()

        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # Check if session_id exists in chat_history, if not add it
        async with db.execute("PRAGMA table_info(chat_history)") as cursor:
            columns = [col[1] for col in await cursor.fetchall()]
            if "session_id" not in columns:
                await db.execute("ALTER TABLE chat_history ADD COLUMN session_id TEXT")
                
        await db.commit()

async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db

from typing import Optional, List, Dict

async def create_user(user: Dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (id, username, password_hash, role) VALUES (?, ?, ?, ?)",
            (user["id"], user["username"], user["password_hash"], user["role"])
        )
        await db.commit()

async def get_user_by_username(username: str) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

async def create_document(doc: Dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO documents (id, filename, chunk_count) VALUES (?, ?, ?)",
            (doc["id"], doc["filename"], doc["chunk_count"])
        )
        await db.commit()

async def get_all_documents() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM documents ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_documents_paginated(limit: int, offset: int, search: str = None) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM documents"
        params = []
        
        if search:
            query += " WHERE filename LIKE ?"
            params.append(f"%{search}%")
            
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with db.execute(query, tuple(params)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_document_count(search: str = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT COUNT(*) FROM documents"
        params = []
        
        if search:
            query += " WHERE filename LIKE ?"
            params.append(f"%{search}%")
            
        async with db.execute(query, tuple(params)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_total_chunks() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT SUM(chunk_count) FROM documents") as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 0

async def delete_document(doc_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        await db.commit()

async def get_all_users() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_users_paginated(limit: int, offset: int, search: str = None, role: str = None) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT id, username, role, created_at FROM users WHERE 1=1"
        params = []
        
        if search:
            query += " AND username LIKE ?"
            params.append(f"%{search}%")
            
        if role:
            query += " AND role = ?"
            params.append(role)
            
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with db.execute(query, tuple(params)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_user_count(search: str = None, role: str = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT COUNT(*) FROM users WHERE 1=1"
        params = []
        
        if search:
            query += " AND username LIKE ?"
            params.append(f"%{search}%")
            
        if role:
            query += " AND role = ?"
            params.append(role)
            
        async with db.execute(query, tuple(params)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def update_user(user_id: str, username: str, role: str, password_hash: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if password_hash:
            await db.execute(
                "UPDATE users SET username = ?, role = ?, password_hash = ? WHERE id = ?",
                (username, role, password_hash, user_id)
            )
        else:
            await db.execute(
                "UPDATE users SET username = ?, role = ? WHERE id = ?",
                (username, role, user_id)
            )
        await db.commit()

async def delete_user(user_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()

async def create_chat_session(session_id: str, user_id: str, title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO chat_sessions (id, user_id, title) VALUES (?, ?, ?)",
            (session_id, user_id, title)
        )
        await db.commit()

async def get_user_sessions(user_id: str) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def update_session_title(session_id: str, title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE chat_sessions SET title = ? WHERE id = ?",
            (title, session_id)
        )
        await db.commit()

async def delete_session(session_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        # Delete all messages in the session
        await db.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        # Delete the session itself
        await db.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        await db.commit()

async def create_chat_message(user_id: str, role: str, content: str, session_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO chat_history (user_id, role, content, session_id) VALUES (?, ?, ?, ?)",
            (user_id, role, content, session_id)
        )
        await db.commit()

async def get_chat_history(session_id: str) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT role, content, created_at FROM chat_history WHERE session_id = ? ORDER BY created_at ASC", 
            (session_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
