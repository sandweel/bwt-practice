from fastapi import Request
from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer
import os

SECRET_KEY = os.getenv("SECRET_KEY", "Fw@lC&#w12v87Fw1O7s")
session_serializer = URLSafeSerializer(SECRET_KEY, salt="session")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_session(user_id: int):
    return session_serializer.dumps({"user_id": user_id})

def get_session_data(session_cookie: str):
    try:
        return session_serializer.loads(session_cookie)
    except Exception:
        return None

def get_current_user(request: Request, db):
    session_token = request.cookies.get("session")
    if not session_token:
        return None
    data = get_session_data(session_token)
    if not data:
        return None
    from dbtools import get_user
    return get_user(db, data["user_id"])
