from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.schemas import EnrollmentCreate

router = APIRouter()

# 1. Enroll Student
@router.post("/")
def enroll_student(enrollment: EnrollmentCreate):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    check_query = """
    SELECT * FROM enrollments 
    WHERE student_id=%s AND subject_id=%s
    """
    cursor.execute(check_query, (enrollment.student_id, enrollment.subject_id))

    if cursor.fetchone():
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="Student already enrolled")

    query = """
    INSERT INTO enrollments (student_id, subject_id)
    VALUES (%s, %s)
    """
    cursor.execute(query, (enrollment.student_id, enrollment.subject_id))
    db.commit()

    cursor.close()
    db.close()
    return {"message": "Enrollment successful"}


# 2. Get all enrollments
@router.get("/")
def get_all_enrollments():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM enrollments")
    data = cursor.fetchall()

    cursor.close()
    db.close()
    return data


# 3. Get enrollments by student id
@router.get("/student/{student_id}")
def get_student_enrollments(student_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM enrollments WHERE student_id=%s"
    cursor.execute(query, (student_id,))
    data = cursor.fetchall()

    cursor.close()
    db.close()
    return data


# 4. Update enrollment
@router.put("/{id}")
def update_enrollment(id: int, enrollment: EnrollmentCreate):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check whether this enrollment exists
    cursor.execute("SELECT * FROM enrollments WHERE id=%s", (id,))
    existing = cursor.fetchone()

    if not existing:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Enrollment not found")

    # Check duplicate with another record
    duplicate_query = """
    SELECT * FROM enrollments
    WHERE student_id=%s AND subject_id=%s AND id != %s
    """
    cursor.execute(
        duplicate_query,
        (enrollment.student_id, enrollment.subject_id, id)
    )
    duplicate = cursor.fetchone()

    if duplicate:
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="Student already enrolled in this subject")

    update_query = """
    UPDATE enrollments
    SET student_id=%s, subject_id=%s
    WHERE id=%s
    """
    cursor.execute(
        update_query,
        (enrollment.student_id, enrollment.subject_id, id)
    )
    db.commit()

    cursor.close()
    db.close()
    return {"message": "Enrollment updated successfully"}


# 5. Delete enrollment
@router.delete("/{id}")
def delete_enrollment(id: int):
    db = get_db_connection()
    cursor = db.cursor()

    query = "DELETE FROM enrollments WHERE id=%s"
    cursor.execute(query, (id,))
    db.commit()

    cursor.close()
    db.close()
    return {"message": "Enrollment deleted"}