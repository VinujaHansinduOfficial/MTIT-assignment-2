from pydantic import BaseModel
from typing import Optional


class TeacherCreate(BaseModel):
    name: str
    email: str
    subject: str


class TeacherResponse(TeacherCreate):
    id: int

    model_config = {"from_attributes": True}


# --- Auth Schemas ---

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# --- Admin Schemas ---

class AdminRegister(BaseModel):
    """Used by an existing admin to create another admin account."""
    username: str
    email: str
    password: str


class PromoteUser(BaseModel):
    """Payload to promote or demote a user's admin status."""
    is_admin: bool

