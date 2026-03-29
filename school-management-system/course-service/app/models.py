from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id          = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True, nullable=False, index=True)
    course_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    credits     = Column(Integer, nullable=False, default=3)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # One course → many subjects
    subjects = relationship("Subject", back_populates="course", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id                   = Column(Integer, primary_key=True, index=True)
    subject_code         = Column(String(20), unique=True, nullable=False, index=True)
    subject_name         = Column(String(100), nullable=False)
    description          = Column(Text, nullable=True)
    credits              = Column(Integer, nullable=False, default=3)
    course_id            = Column(Integer, ForeignKey("courses.id"), nullable=False)
    assigned_teacher_id  = Column(Integer, nullable=True)   # reference to Teacher Service
    assigned_teacher_name= Column(String(100), nullable=True)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())
    updated_at           = Column(DateTime(timezone=True), onupdate=func.now())

    # Many subjects → one course
    course = relationship("Course", back_populates="subjects")
