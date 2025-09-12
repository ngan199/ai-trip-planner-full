# Purpose: JWT-based auth; use typed Settings attributes (no dict())
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from .database import get_session
from .models_db import User
from .settings import Settings

router = APIRouter(prefix="/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
s = Settings()  # typed settings

class RegisterIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

def hash_password(pw: str) -> str:
    return pwd.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return pwd.verify(pw, hashed)

def create_access_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=s.jwt_expire_minutes)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_alg)

async def get_current_user(session: AsyncSession = Depends(get_session), token: str | None = None) -> User | None:
    """Optional auth: return User if valid token provided; otherwise None."""
    if not token:
        return None
    try:
        data = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_alg])
        email = data.get("sub")
        if not email:
            return None
    except JWTError:
        return None
    q = await session.execute(select(User).where(User.email == email))
    return q.scalar_one_or_none()

@router.post("/register", response_model=TokenOut)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_session)):
    q = await session.execute(select(User).where(User.email == body.email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=body.email, password_hash=hash_password(body.password))
    session.add(user)
    await session.commit()
    token = create_access_token(body.email)
    return TokenOut(access_token=token, expires_in=s.jwt_expire_minutes * 60)

@router.post("/login", response_model=TokenOut)
async def login(body: RegisterIn, session: AsyncSession = Depends(get_session)):
    q = await session.execute(select(User).where(User.email == body.email))
    user = q.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(body.email)
    return TokenOut(access_token=token, expires_in=s.jwt_expire_minutes * 60)
