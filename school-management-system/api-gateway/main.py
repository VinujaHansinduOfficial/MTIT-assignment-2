from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx

app = FastAPI(
    title="School Management API Gateway",
    description="Gateway for Student, Teacher, Course, Subject, and Enrollment services",
    version="1.0.0"
)

# -----------------------------
# Service URLs
# -----------------------------
STUDENT_SERVICE = "http://127.0.0.1:8001"
TEACHER_SERVICE = "http://127.0.0.1:8002"
COURSE_SERVICE = "http://127.0.0.1:8003"
ENROLLMENT_SERVICE = "http://127.0.0.1:8004"


# -----------------------------
# Request Schemas
# -----------------------------
class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    age: int


class StudentUpdate(BaseModel):
    name: str
    email: EmailStr
    age: int


class TeacherCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str


class TeacherUpdate(BaseModel):
    name: str
    email: EmailStr
    subject: str


class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    description: Optional[str] = None
    credits: int


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None


class SubjectCreate(BaseModel):
    subject_code: str
    subject_name: str
    description: Optional[str] = None
    credits: int
    course_id: int


class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None


class AssignTeacherRequest(BaseModel):
    teacher_id: int
    teacher_name: str


class EnrollmentCreate(BaseModel):
    student_id: int
    subject_id: int


# -----------------------------
# Helper
# -----------------------------
async def forward_request(method: str, url: str, json_data=None):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                json=json_data
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Target service unavailable")


@app.get("/")
def root():
    return {
        "message": "School Management API Gateway is running",
        "services": {
            "students": STUDENT_SERVICE,
            "teachers": TEACHER_SERVICE,
            "courses": COURSE_SERVICE,
            "subjects": COURSE_SERVICE,
            "enrollments": ENROLLMENT_SERVICE,
        }
    }


# =====================================================
# STUDENT SERVICE
# =====================================================
@app.get("/students", summary="Get all students")
async def get_students():
    return await forward_request("GET", f"{STUDENT_SERVICE}/students")


@app.get("/students/{id}", summary="Get student by ID")
async def get_student(id: int):
    return await forward_request("GET", f"{STUDENT_SERVICE}/students/{id}")


@app.post("/students", summary="Create student")
async def create_student(student: StudentCreate):
    return await forward_request(
        "POST",
        f"{STUDENT_SERVICE}/students",
        json_data=student.model_dump()
    )


@app.put("/students/{id}", summary="Update student")
async def update_student(id: int, student: StudentUpdate):
    return await forward_request(
        "PUT",
        f"{STUDENT_SERVICE}/students/{id}",
        json_data=student.model_dump()
    )


@app.delete("/students/{id}", summary="Delete student")
async def delete_student(id: int):
    return await forward_request("DELETE", f"{STUDENT_SERVICE}/students/{id}")


# =====================================================
# TEACHER SERVICE
# =====================================================
@app.get("/teachers", summary="Get all teachers")
async def get_teachers():
    return await forward_request("GET", f"{TEACHER_SERVICE}/teachers")


@app.post("/teachers", summary="Create teacher")
async def create_teacher(teacher: TeacherCreate):
    return await forward_request(
        "POST",
        f"{TEACHER_SERVICE}/teachers",
        json_data=teacher.model_dump()
    )


@app.put("/teachers/{id}", summary="Update teacher")
async def update_teacher(id: int, teacher: TeacherUpdate):
    return await forward_request(
        "PUT",
        f"{TEACHER_SERVICE}/teachers/{id}",
        json_data=teacher.model_dump()
    )


@app.delete("/teachers/{id}", summary="Delete teacher")
async def delete_teacher(id: int):
    return await forward_request("DELETE", f"{TEACHER_SERVICE}/teachers/{id}")


# =====================================================
# COURSE SERVICE
# =====================================================
@app.get("/courses", summary="Get all courses")
async def get_courses(skip: int = 0, limit: int = 100):
    return await forward_request(
        "GET",
        f"{COURSE_SERVICE}/courses/?skip={skip}&limit={limit}"
    )


@app.get("/courses/{course_id}", summary="Get course by ID")
async def get_course(course_id: int):
    return await forward_request("GET", f"{COURSE_SERVICE}/courses/{course_id}")


@app.post("/courses", summary="Create course")
async def create_course(course: CourseCreate):
    return await forward_request(
        "POST",
        f"{COURSE_SERVICE}/courses/",
        json_data=course.model_dump()
    )


@app.put("/courses/{course_id}", summary="Update course")
async def update_course(course_id: int, course: CourseUpdate):
    return await forward_request(
        "PUT",
        f"{COURSE_SERVICE}/courses/{course_id}",
        json_data=course.model_dump(exclude_unset=True)
    )


@app.delete("/courses/{course_id}", summary="Delete course")
async def delete_course(course_id: int):
    return await forward_request("DELETE", f"{COURSE_SERVICE}/courses/{course_id}")


# =====================================================
# SUBJECT SERVICE
# =====================================================
@app.get("/subjects", summary="Get all subjects")
async def get_subjects(skip: int = 0, limit: int = 100):
    return await forward_request(
        "GET",
        f"{COURSE_SERVICE}/subjects/?skip={skip}&limit={limit}"
    )


@app.get("/subjects/{subject_id}", summary="Get subject by ID")
async def get_subject(subject_id: int):
    return await forward_request("GET", f"{COURSE_SERVICE}/subjects/{subject_id}")


@app.get("/subjects/by-course/{course_id}", summary="Get subjects by course")
async def get_subjects_by_course(course_id: int):
    return await forward_request("GET", f"{COURSE_SERVICE}/subjects/by-course/{course_id}")


@app.post("/subjects", summary="Create subject")
async def create_subject(subject: SubjectCreate):
    return await forward_request(
        "POST",
        f"{COURSE_SERVICE}/subjects/",
        json_data=subject.model_dump()
    )


@app.put("/subjects/{subject_id}", summary="Update subject")
async def update_subject(subject_id: int, subject: SubjectUpdate):
    return await forward_request(
        "PUT",
        f"{COURSE_SERVICE}/subjects/{subject_id}",
        json_data=subject.model_dump(exclude_unset=True)
    )


@app.patch("/subjects/{subject_id}/assign-teacher", summary="Assign teacher to subject")
async def assign_teacher(subject_id: int, data: AssignTeacherRequest):
    return await forward_request(
        "PATCH",
        f"{COURSE_SERVICE}/subjects/{subject_id}/assign-teacher",
        json_data=data.model_dump()
    )


@app.patch("/subjects/{subject_id}/remove-teacher", summary="Remove teacher from subject")
async def remove_teacher(subject_id: int):
    return await forward_request(
        "PATCH",
        f"{COURSE_SERVICE}/subjects/{subject_id}/remove-teacher"
    )


@app.delete("/subjects/{subject_id}", summary="Delete subject")
async def delete_subject(subject_id: int):
    return await forward_request("DELETE", f"{COURSE_SERVICE}/subjects/{subject_id}")


# =====================================================
# ENROLLMENT SERVICE
# =====================================================
@app.get("/enrollments", summary="Get all enrollments")
async def get_enrollments():
    return await forward_request("GET", f"{ENROLLMENT_SERVICE}/")


@app.get("/enrollments/student/{student_id}", summary="Get enrollments by student ID")
async def get_student_enrollments(student_id: int):
    return await forward_request("GET", f"{ENROLLMENT_SERVICE}/student/{student_id}")


@app.post("/enrollments", summary="Enroll student")
async def enroll_student(enrollment: EnrollmentCreate):
    return await forward_request(
        "POST",
        f"{ENROLLMENT_SERVICE}/",
        json_data=enrollment.model_dump()
    )


@app.delete("/enrollments/{id}", summary="Delete enrollment")
async def delete_enrollment(id: int):
    return await forward_request("DELETE", f"{ENROLLMENT_SERVICE}/{id}")