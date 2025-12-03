import asyncio
import sys
import os

# Add the current directory to sys.path to allow importing backend modules
sys.path.append(os.getcwd())

from backend.services.sqlite_client import create_user, init_db
from backend.utils.security import get_password_hash
import uuid

async def main():
    print("Creating Admin User...")
    # Ensure DB is initialized
    await init_db()
    
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    
    user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password_hash": get_password_hash(password),
        "role": "admin"
    }
    
    try:
        await create_user(user)
        print(f"\nSUCCESS: Admin user '{username}' created!")
        print("You can now login at http://localhost:5173/login")
    except Exception as e:
        print(f"\nERROR: Could not create user. {e}")

if __name__ == "__main__":
    asyncio.run(main())
