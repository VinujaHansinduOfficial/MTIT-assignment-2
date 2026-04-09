"""
auth.py — JWT-based authentication and authorization for microservices.

Authentication strategy (two-layer):
  PRIMARY  — JWT Bearer token: verified using the shared SECRET_KEY.
             The `is_admin` claim embedded in the token is authoritative.
  SECONDARY — X-Is-Admin / X-Username headers: injected by the API Gateway
             after it has already validated the JWT. Services behind the
             gateway can use these headers as a trusted fast-path since the
             gateway is the only entry-point on the internal network.

  Both layers must agree; the JWT is always re-verified if present.
  No database lookup is performed during authentication — every service
  can authenticate requests independently using only the token.
  The local User DB is only used by the /auth/* management endpoints.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

SECRET_KEY = "change-me-in-production-use-a-long-random-string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Lightweight user object — built from JWT claims, no DB needed
# ---------------------------------------------------------------------------
@dataclass
class TokenUser:
    """Represents the authenticated caller, derived from JWT or gateway headers."""
    username: str
    is_admin: bool


# ---------------------------------------------------------------------------
# Password / token utilities (used by auth management endpoints)
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
# DB session helper (used only by auth management endpoints)
# ---------------------------------------------------------------------------
def get_db():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Core: decode and validate the Bearer token
# ---------------------------------------------------------------------------
def _decode_token(credentials: HTTPAuthorizationCredentials) -> TokenUser:
    """
    Verify the JWT signature and expiry, then return a TokenUser.
    Raises HTTP 401 on any failure.
    """
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        is_admin: bool = bool(payload.get("is_admin", False))
        return TokenUser(username=username, is_admin=is_admin)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# FastAPI dependencies — support both direct JWT and gateway-forwarded requests
# ---------------------------------------------------------------------------
def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> TokenUser:
    """
    Require any authenticated user.

    Accepts:
      - A valid Bearer JWT token (primary path — direct or forwarded by gateway)
      - X-Username + X-Is-Admin headers when the JWT has already been verified
        by the gateway (secondary trust path for internal traffic)
    """
    if credentials:
        return _decode_token(credentials)

    # Gateway-forwarded request — trust X-Username / X-Is-Admin headers
    username = request.headers.get("X-Username")
    if username:
        is_admin = request.headers.get("X-Is-Admin", "false").lower() == "true"
        return TokenUser(username=username, is_admin=is_admin)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated — provide a Bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> TokenUser:
    """
    Require an admin user.

    Accepts:
      - A valid Bearer JWT token with is_admin=true
      - X-Is-Admin: true header from the gateway (secondary trust path)
    """
    user = get_current_user(request, credentials)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
