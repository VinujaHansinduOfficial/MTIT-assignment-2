from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/teachers")
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    new_teacher = models.Teacher(**teacher.dict())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@router.get("/teachers")
def get_teachers(db: Session = Depends(get_db)):
    return db.query(models.Teacher).all()


@router.put("/teachers/{id}")
def update_teacher(id: int, teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    t = db.query(models.Teacher).filter(models.Teacher.id == id).first()
    t.name = teacher.name
    t.email = teacher.email
    t.subject = teacher.subject
    db.commit()
    return t


@router.delete("/teachers/{id}")
def delete_teacher(id: int, db: Session = Depends(get_db)):
    t = db.query(models.Teacher).filter(models.Teacher.id == id).first()
    db.delete(t)
    db.commit()
    return {"message": "Deleted"}