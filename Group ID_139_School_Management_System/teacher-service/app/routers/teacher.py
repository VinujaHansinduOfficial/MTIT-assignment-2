from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, database
from ..auth import get_current_user, get_current_admin, TokenUser

router = APIRouter(tags=["teachers"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/teachers",
    status_code=status.HTTP_201_CREATED,
    summary="Create a teacher (admin only)",
)
def create_teacher(
    teacher: schemas.TeacherCreate,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    new_teacher = models.Teacher(**teacher.dict())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@router.get(
    "/teachers",
    summary="List all teachers (any authenticated user)",
)
def get_teachers(
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_user),
):
    return db.query(models.Teacher).all()


@router.get(
    "/teachers/{id}",
    summary="Get a teacher by ID (any authenticated user)",
)
def get_teacher(
    id: int,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_user),
):
    t = db.query(models.Teacher).filter(models.Teacher.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return t


@router.put(
    "/teachers/{id}",
    summary="Update a teacher (admin only)",
)
def update_teacher(
    id: int,
    teacher: schemas.TeacherCreate,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    t = db.query(models.Teacher).filter(models.Teacher.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    t.name = teacher.name
    t.email = teacher.email
    t.subject = teacher.subject
    db.commit()
    return t


@router.delete(
    "/teachers/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a teacher (admin only)",
)
def delete_teacher(
    id: int,
    db: Session = Depends(get_db),
    _: TokenUser = Depends(get_current_admin),
):
    t = db.query(models.Teacher).filter(models.Teacher.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(t)
    db.commit()

