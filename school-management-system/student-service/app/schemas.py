from pydantic import BaseModel

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
        orm_mode = True
