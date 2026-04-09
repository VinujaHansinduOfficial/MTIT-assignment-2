from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal
from app.auth import get_current_user, get_current_admin, TokenUser

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE student — admin only
@router.post("/students", response_model=schemas.StudentResponse)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


# GET all students — any authenticated user
@router.get("/students", response_model=list[schemas.StudentResponse])
def get_students(
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_user),
):
    return db.query(models.Student).all()


# GET single student — any authenticated user
@router.get("/students/{id}", response_model=schemas.StudentResponse)
def get_student(
    id: int,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# UPDATE student — admin only
@router.put("/students/{id}", response_model=schemas.StudentResponse)
def update_student(
    id: int,
    updated_data: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    student = db.query(models.Student).filter(models.Student.id == id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = updated_data.name
    student.email = updated_data.email
    student.age = updated_data.age

    db.commit()
    db.refresh(student)

    return student


# DELETE student — admin only
@router.delete("/students/{id}")
def delete_student(
    id: int,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    student = db.query(models.Student).filter(models.Student.id == id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()

    return {"message": "Deleted successfully"}

