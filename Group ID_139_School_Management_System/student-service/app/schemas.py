from pydantic import BaseModel
from typing import Optional


class StudentBase(BaseModel):
    name: str
    email: str
    age: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class AdminRegister(BaseModel):
    username: str
    email: str
    password: str


class PromoteUser(BaseModel):
    is_admin: bool
