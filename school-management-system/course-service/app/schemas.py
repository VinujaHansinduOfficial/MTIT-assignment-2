from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Course Schemas ────────────────────────────────────────────────────────────

class CourseBase(BaseModel):
    course_code: str        = Field(..., example="CS101")
    course_name: str        = Field(..., example="Computer Science")
    description: Optional[str] = Field(None, example="Fundamentals of Computer Science")
    credits: int            = Field(default=3, ge=1, le=10, example=3)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_name: Optional[str]  = Field(None, example="Advanced Computer Science")
    description: Optional[str]  = Field(None, example="Updated description")
    credits: Optional[int]      = Field(None, ge=1, le=10, example=4)


class CourseResponse(CourseBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CourseWithSubjects(CourseResponse):
    subjects: List["SubjectResponse"] = []

    class Config:
        from_attributes = True


# ─── Subject Schemas ───────────────────────────────────────────────────────────

class SubjectBase(BaseModel):
    subject_code: str          = Field(..., example="CS101-S1")
    subject_name: str          = Field(..., example="Introduction to Programming")
    description: Optional[str] = Field(None, example="Basic programming concepts using Python")
    credits: int               = Field(default=3, ge=1, le=10, example=3)
    course_id: int             = Field(..., example=1)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = Field(None, example="Advanced Programming")
    description: Optional[str]  = Field(None, example="Updated description")
    credits: Optional[int]      = Field(None, ge=1, le=10, example=4)


class AssignTeacherRequest(BaseModel):
    teacher_id: int    = Field(..., example=5)
    teacher_name: str  = Field(..., example="Dr. John Smith")


class SubjectResponse(SubjectBase):
    id: int
    assigned_teacher_id: Optional[int]
    assigned_teacher_name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── Generic Response ──────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True
