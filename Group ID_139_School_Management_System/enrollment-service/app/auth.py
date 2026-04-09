from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "change-me-in-production-use-a-long-random-string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Lightweight user representation — replaces models.User for gateway traffic
# ---------------------------------------------------------------------------
@dataclass
class GatewayUser:
    """Populated from gateway-injected headers; no DB lookup needed."""
    username: str
    is_admin: bool


# ---------------------------------------------------------------------------
# Password / token utilities (kept for the local auth routers)
# ---------------------------------------------------------------------------
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# DB session helper (kept so local auth routers can still import get_db)
# ---------------------------------------------------------------------------
def get_db():
    # Import here to avoid a circular import; the DB module is service-specific
    try:
        from app.database import SessionLocal          # student / course / enrollment
    except ImportError:
        from .database import SessionLocal             # teacher (relative import)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Auth dependencies — used by every protected router
# ---------------------------------------------------------------------------
def _extract_user(request: Request) -> GatewayUser:
    """
    1. If the API gateway injected X-Username / X-Is-Admin headers → trust them.
       (The gateway validates the JWT before forwarding, so no re-validation needed.)
    2. Fallback: decode the Bearer token directly.
       (Allows hitting the service without the gateway, e.g. local dev / tests.)
    """
    username = request.headers.get("X-Username")
    if username:
        is_admin = request.headers.get("X-Is-Admin", "false").lower() == "true"
        return GatewayUser(username=username, is_admin=is_admin)

    # Fallback path
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        return GatewayUser(username=sub, is_admin=bool(payload.get("is_admin", False)))
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(request: Request) -> GatewayUser:
    """Require any authenticated user."""
    return _extract_user(request)


def get_current_admin(request: Request) -> GatewayUser:
    """Require an admin user."""
    user = _extract_user(request)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
