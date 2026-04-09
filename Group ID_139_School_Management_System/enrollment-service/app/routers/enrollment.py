from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, get_current_admin, TokenUser

router = APIRouter()


# 1. Enroll Student — admin only
@router.post("/", status_code=status.HTTP_201_CREATED)
def enroll_student(
    enrollment: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    existing = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == enrollment.student_id,
        models.Enrollment.subject_id == enrollment.subject_id,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")

    new_enrollment = models.Enrollment(
        student_id=enrollment.student_id,
        subject_id=enrollment.subject_id,
    )
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return {"message": "Enrollment successful", "id": new_enrollment.id}


# 2. Get all enrollments — any authenticated user
@router.get("/", response_model=list[schemas.EnrollmentResponse])
def get_all_enrollments(
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_user),
):
    return db.query(models.Enrollment).all()


# 3. Get enrollments by student id — any authenticated user
@router.get("/student/{student_id}", response_model=list[schemas.EnrollmentResponse])
def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_user),
):
    return db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student_id
    ).all()


# 4. Update enrollment — admin only
@router.put("/{id}")
def update_enrollment(
    id: int,
    enrollment: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    existing = db.query(models.Enrollment).filter(models.Enrollment.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    duplicate = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == enrollment.student_id,
        models.Enrollment.subject_id == enrollment.subject_id,
        models.Enrollment.id != id,
    ).first()

    if duplicate:
        raise HTTPException(status_code=400, detail="Student already enrolled in this subject")

    existing.student_id = enrollment.student_id
    existing.subject_id = enrollment.subject_id
    db.commit()
    return {"message": "Enrollment updated successfully"}


# 5. Delete enrollment — admin only
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(
    id: int,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()
