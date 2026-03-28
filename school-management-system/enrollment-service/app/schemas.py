from pydantic import BaseModel

class EnrollmentCreate(BaseModel):
    student_id: int
    subject_id: int