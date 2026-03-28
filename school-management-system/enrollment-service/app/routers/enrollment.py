from fastapi import APIRouter
from app.database import get_db_connection
from app.schemas import EnrollmentCreate

router = APIRouter()

# 1. Enroll Student
@router.post("/")
def enroll_student(enrollment: EnrollmentCreate):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check duplicate
    check_query = """
    SELECT * FROM enrollments 
    WHERE student_id=%s AND subject_id=%s
    """
    cursor.execute(check_query, (enrollment.student_id, enrollment.subject_id))

    if cursor.fetchone():
        return {"error": "Student already enrolled"}

    query = """
    INSERT INTO enrollments (student_id, subject_id)
    VALUES (%s, %s)
    """
    cursor.execute(query, (enrollment.student_id, enrollment.subject_id))
    db.commit()

    return {"message": "Enrollment successful"} 

#2.get all enrollments
@router.get("/")
def get_all_enrollments():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM enrollments")
    return cursor.fetchall()

#3.get enrollments by student id
@router.get("/student/{student_id}")
def get_student_enrollments(student_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM enrollments WHERE student_id=%s"
    cursor.execute(query, (student_id,))

    return cursor.fetchall()

#4.delete enrollment
@router.delete("/{id}")
def delete_enrollment(id: int):
    db = get_db_connection()
    cursor = db.cursor()

    query = "DELETE FROM enrollments WHERE id=%s"
    cursor.execute(query, (id,))
    db.commit()

    return {"message": "Enrollment deleted"}