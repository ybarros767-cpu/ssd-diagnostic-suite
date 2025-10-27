from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from settings import settings

router = APIRouter(tags=["auth"])

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"


def _is_bcrypt_hash(value: str) -> bool:
    return value.startswith("$2a$") or value.startswith("$2b$") or value.startswith("$2y$")


def verify_password(plain_password: str, hashed_or_plain: str) -> bool:
    if _is_bcrypt_hash(hashed_or_plain):
        return password_context.verify(plain_password, hashed_or_plain)
    return plain_password == hashed_or_plain


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    if username != settings.admin_username:
        return None
    if not verify_password(password, settings.admin_password):
        return None
    return {"username": username, "role": "admin"}


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_exp_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": "ssd-diagnostic-suite",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    return token


@router.post("/auth/login")
def login(body: Dict[str, str]) -> Dict[str, str]:
    if not settings.enable_auth:
        # Auth desabilitada; retorna token de convidado para compatibilidade
        token = create_access_token("guest", "viewer")
        return {"access_token": token, "token_type": "bearer"}

    username = body.get("username", "").strip()
    password = body.get("password", "")

    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    token = create_access_token(user["username"], user["role"])
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    if not settings.enable_auth:
        return {"username": "anonymous", "role": "viewer"}

    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        role: str = payload.get("role", "viewer")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
