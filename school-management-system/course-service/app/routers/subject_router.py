from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Subject, Course
from app.schemas import (
    SubjectCreate, SubjectUpdate,
    SubjectResponse, AssignTeacherRequest, MessageResponse,
)

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
)


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new subject under a course")
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    if not db.query(Course).filter(Course.id == subject.course_id).first():
        raise HTTPException(status_code=404,
                            detail=f"Course ID {subject.course_id} not found.")
    if db.query(Subject).filter(Subject.subject_code == subject.subject_code).first():
        raise HTTPException(status_code=400,
                            detail=f"Subject code '{subject.subject_code}' already exists.")
    new_subject = Subject(**subject.model_dump())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject


@router.get("/", response_model=List[SubjectResponse], summary="Get all subjects")
def get_all_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Subject).offset(skip).limit(limit).all()


@router.get("/by-course/{course_id}", response_model=List[SubjectResponse],
            summary="Get all subjects under a specific course")
def get_subjects_by_course(course_id: int, db: Session = Depends(get_db)):
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(status_code=404, detail=f"Course ID {course_id} not found.")
    return db.query(Subject).filter(Subject.course_id == course_id).all()


@router.get("/{subject_id}", response_model=SubjectResponse, summary="Get a subject by ID")
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject ID {subject_id} not found.")
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse, summary="Update a subject")
def update_subject(subject_id: int, data: SubjectUpdate, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject ID {subject_id} not found.")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(subject, k, v)
    db.commit()
    db.refresh(subject)
    return subject


@router.patch("/{subject_id}/assign-teacher", response_model=SubjectResponse,
              summary="Assign a teacher to a subject")
def assign_teacher(subject_id: int, data: AssignTeacherRequest,
                   db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject ID {subject_id} not found.")
    subject.assigned_teacher_id   = data.teacher_id
    subject.assigned_teacher_name = data.teacher_name
    db.commit()
    db.refresh(subject)
    return subject


@router.patch("/{subject_id}/remove-teacher", response_model=SubjectResponse,
              summary="Remove the assigned teacher from a subject")
def remove_teacher(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject ID {subject_id} not found.")
    subject.assigned_teacher_id   = None
    subject.assigned_teacher_name = None
    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}", response_model=MessageResponse, summary="Delete a subject")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject ID {subject_id} not found.")
    db.delete(subject)
    db.commit()
    return {"message": f"Subject '{subject.subject_name}' deleted.", "success": True}
