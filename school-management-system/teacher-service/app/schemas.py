from pydantic import BaseModel

class TeacherCreate(BaseModel):
    name: str
    email: str
    subject: str

class TeacherResponse(TeacherCreate):
    id: int

    class Config:
        orm_mode = True