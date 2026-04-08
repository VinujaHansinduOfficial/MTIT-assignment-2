from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Course
from app.schemas import (
    CourseCreate, CourseUpdate,
    CourseResponse, CourseWithSubjects, MessageResponse,
)

router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new course")
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    existing = db.query(Course).filter(Course.course_code == course.course_code).first()
    if existing:
        raise HTTPException(status_code=400,
                            detail=f"Course code '{course.course_code}' already exists.")
    new_course = Course(**course.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/", response_model=List[CourseResponse], summary="Get all courses")
def get_all_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Course).offset(skip).limit(limit).all()


@router.get("/{course_id}", response_model=CourseWithSubjects,
            summary="Get a course by ID — includes its subjects")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course ID {course_id} not found.")
    return course


@router.put("/{course_id}", response_model=CourseResponse, summary="Update a course")
def update_course(course_id: int, data: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course ID {course_id} not found.")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", response_model=MessageResponse, summary="Delete a course")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course ID {course_id} not found.")
    db.delete(course)
    db.commit()
    return {"message": f"Course '{course.course_name}' deleted.", "success": True}
