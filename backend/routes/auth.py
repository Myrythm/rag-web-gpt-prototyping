from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.utils.security import create_access_token, verify_password, get_password_hash
from backend.services.sqlite_client import get_user_by_username, create_user, get_user_count
from backend.utils.config import settings
import uuid

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    # Simple register for demo purposes
    existing_user = await get_user_by_username(form_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(form_data.password)
    
    # Check if this is the first user
    user_count = await get_user_count()
    role = "admin" if user_count == 0 else "user" 
    
    user_data = {
        "id": user_id,
        "username": form_data.username,
        "password_hash": hashed_password,
        "role": role
    }
    await create_user(user_data)
    return {"msg": "User created successfully"}
