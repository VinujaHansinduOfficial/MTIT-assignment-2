from fastapi import FastAPI, Response, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
from jose import JWTError, jwt

# Must match the SECRET_KEY used in all microservices
SECRET_KEY = "change-me-in-production-use-a-long-random-string"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(
    title="School Management API Gateway",
    description="Gateway for Student, Teacher, Course, Subject, Enrollment, and Auth services",
    version="1.0.0"
)

# -----------------------------
# Service URLs
# -----------------------------
STUDENT_SERVICE    = "http://127.0.0.1:8001"
TEACHER_SERVICE    = "http://127.0.0.1:8002"
COURSE_SERVICE     = "http://127.0.0.1:8003"
ENROLLMENT_SERVICE = "http://127.0.0.1:8004"
AUTH_SERVICE       = "http://127.0.0.1:8002"   # auth lives in teacher-service


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

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AdminRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class PromoteUser(BaseModel):
    is_admin: bool


# -----------------------------
# JWT Helper — validate token in the gateway
# -----------------------------
def decode_token(token: str) -> dict:
    """
    Verify the JWT signature and expiry.
    Returns the payload dict on success; raises HTTP 401 on any failure.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# -----------------------------
# Dependency — require a valid Bearer token
# -----------------------------
def get_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated — provide a Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# -----------------------------
# Core forward helper
# -----------------------------
async def forward_request(
    method: str,
    url: str,
    request: Request | None = None,
    json_data=None,
    token: str | None = None,
):
    """
    Forward a request to a downstream microservice.

    When `token` is provided the gateway:
      1. Validates the JWT (raises 401/403 early if bad).
      2. Injects gateway-signed headers so downstream services do NOT need
         to look up the user in their own database:
            Authorization : Bearer <original token>   (kept for compat)
            X-Username    : <sub claim>
            X-Is-Admin    : "true" | "false"

    Downstream services trust these headers because they are only reachable
    from the gateway on the internal network.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            headers: dict[str, str] = {}

            if token:
                payload = decode_token(token)
                headers["Authorization"] = f"Bearer {token}"
                headers["X-Username"]    = payload.get("sub", "")
                headers["X-Is-Admin"]    = str(payload.get("is_admin", False)).lower()
            elif request:
                # Public routes (/auth/register, /auth/login) — pass through as-is
                authorization = request.headers.get("authorization")
                if authorization:
                    headers["authorization"] = authorization

            response = await client.request(
                method=method,
                url=url,
                json=json_data,
                headers=headers,
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json"),
            )

        except HTTPException:
            raise
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Target service unavailable: {str(e)}"
            )


@app.get("/")
def root():
    return {
        "message": "School Management API Gateway is running",
        "services": {
            "students":    STUDENT_SERVICE,
            "teachers":    TEACHER_SERVICE,
            "courses":     COURSE_SERVICE,
            "subjects":    COURSE_SERVICE,
            "enrollments": ENROLLMENT_SERVICE,
            "auth":        AUTH_SERVICE,
        },
    }


# =====================================================
# STUDENT SERVICE
# =====================================================
@app.get("/students")
async def get_students(request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{STUDENT_SERVICE}/students", request=request, token=token)

@app.get("/students/{id}")
async def get_student(id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{STUDENT_SERVICE}/students/{id}", request=request, token=token)

@app.post("/students")
async def create_student(student: StudentCreate, request: Request, token: str = Depends(get_token)):
    return await forward_request("POST", f"{STUDENT_SERVICE}/students", request=request,
                                 json_data=student.model_dump(), token=token)

@app.put("/students/{id}")
async def update_student(id: int, student: StudentUpdate, request: Request, token: str = Depends(get_token)):
    return await forward_request("PUT", f"{STUDENT_SERVICE}/students/{id}", request=request,
                                 json_data=student.model_dump(), token=token)

@app.delete("/students/{id}")
async def delete_student(id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("DELETE", f"{STUDENT_SERVICE}/students/{id}", request=request, token=token)


# =====================================================
# TEACHER SERVICE
# =====================================================
@app.get("/teachers")
async def get_teachers(request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{TEACHER_SERVICE}/teachers", request=request, token=token)

@app.post("/teachers")
async def create_teacher(teacher: TeacherCreate, request: Request, token: str = Depends(get_token)):
    return await forward_request("POST", f"{TEACHER_SERVICE}/teachers", request=request,
                                 json_data=teacher.model_dump(), token=token)

@app.put("/teachers/{id}")
async def update_teacher(id: int, teacher: TeacherUpdate, request: Request, token: str = Depends(get_token)):
    return await forward_request("PUT", f"{TEACHER_SERVICE}/teachers/{id}", request=request,
                                 json_data=teacher.model_dump(), token=token)

@app.delete("/teachers/{id}")
async def delete_teacher(id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("DELETE", f"{TEACHER_SERVICE}/teachers/{id}", request=request, token=token)


# =====================================================
# COURSE SERVICE
# =====================================================
@app.get("/courses")
async def get_courses(request: Request, token: str = Depends(get_token), skip: int = 0, limit: int = 100):
    return await forward_request("GET", f"{COURSE_SERVICE}/courses/?skip={skip}&limit={limit}",
                                 request=request, token=token)

@app.get("/courses/{course_id}")
async def get_course(course_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{COURSE_SERVICE}/courses/{course_id}", request=request, token=token)

@app.post("/courses")
async def create_course(course: CourseCreate, request: Request, token: str = Depends(get_token)):
    return await forward_request("POST", f"{COURSE_SERVICE}/courses/", request=request,
                                 json_data=course.model_dump(), token=token)

@app.put("/courses/{course_id}")
async def update_course(course_id: int, course: CourseUpdate, request: Request, token: str = Depends(get_token)):
    return await forward_request("PUT", f"{COURSE_SERVICE}/courses/{course_id}", request=request,
                                 json_data=course.model_dump(exclude_unset=True), token=token)

@app.delete("/courses/{course_id}")
async def delete_course(course_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("DELETE", f"{COURSE_SERVICE}/courses/{course_id}", request=request, token=token)


# =====================================================
# SUBJECT SERVICE
# =====================================================
@app.get("/subjects")
async def get_subjects(request: Request, token: str = Depends(get_token), skip: int = 0, limit: int = 100):
    return await forward_request("GET", f"{COURSE_SERVICE}/subjects/?skip={skip}&limit={limit}",
                                 request=request, token=token)

@app.get("/subjects/{subject_id}")
async def get_subject(subject_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{COURSE_SERVICE}/subjects/{subject_id}", request=request, token=token)

@app.get("/subjects/by-course/{course_id}")
async def get_subjects_by_course(course_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{COURSE_SERVICE}/subjects/by-course/{course_id}",
                                 request=request, token=token)

@app.post("/subjects")
async def create_subject(subject: SubjectCreate, request: Request, token: str = Depends(get_token)):
    return await forward_request("POST", f"{COURSE_SERVICE}/subjects/", request=request,
                                 json_data=subject.model_dump(), token=token)

@app.put("/subjects/{subject_id}")
async def update_subject(subject_id: int, subject: SubjectUpdate, request: Request, token: str = Depends(get_token)):
    return await forward_request("PUT", f"{COURSE_SERVICE}/subjects/{subject_id}", request=request,
                                 json_data=subject.model_dump(exclude_unset=True), token=token)

@app.patch("/subjects/{subject_id}/assign-teacher")
async def assign_teacher(subject_id: int, data: AssignTeacherRequest, request: Request, token: str = Depends(get_token)):
    return await forward_request("PATCH", f"{COURSE_SERVICE}/subjects/{subject_id}/assign-teacher",
                                 request=request, json_data=data.model_dump(), token=token)

@app.patch("/subjects/{subject_id}/remove-teacher")
async def remove_teacher(subject_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("PATCH", f"{COURSE_SERVICE}/subjects/{subject_id}/remove-teacher",
                                 request=request, token=token)

@app.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("DELETE", f"{COURSE_SERVICE}/subjects/{subject_id}", request=request, token=token)


# =====================================================
# ENROLLMENT SERVICE
# =====================================================
@app.get("/enrollments")
async def get_enrollments(request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{ENROLLMENT_SERVICE}/enrollments/", request=request, token=token)

@app.get("/enrollments/student/{student_id}")
async def get_student_enrollments(student_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{ENROLLMENT_SERVICE}/enrollments/student/{student_id}",
                                 request=request, token=token)

@app.post("/enrollments")
async def enroll_student(enrollment: EnrollmentCreate, request: Request, token: str = Depends(get_token)):
    return await forward_request("POST", f"{ENROLLMENT_SERVICE}/enrollments/", request=request,
                                 json_data=enrollment.model_dump(), token=token)

@app.put("/enrollments/{id}")
async def update_enrollment(id: int, enrollment: EnrollmentCreate, request: Request, token: str = Depends(get_token)):
    return await forward_request("PUT", f"{ENROLLMENT_SERVICE}/enrollments/{id}", request=request,
                                 json_data=enrollment.model_dump(), token=token)

@app.delete("/enrollments/{id}")
async def delete_enrollment(id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("DELETE", f"{ENROLLMENT_SERVICE}/enrollments/{id}", request=request, token=token)


# =====================================================
# AUTH SERVICE  (login/register are public — no token needed)
# =====================================================
@app.post("/auth/register")
async def register_user(data: UserRegister, request: Request):
    return await forward_request("POST", f"{AUTH_SERVICE}/auth/register",
                                 request=request, json_data=data.model_dump())

@app.post("/auth/login")
async def login_user(data: UserLogin, request: Request):
    return await forward_request("POST", f"{AUTH_SERVICE}/auth/login",
                                 request=request, json_data=data.model_dump())

@app.post("/auth/admin/register")
async def register_admin(data: AdminRegister, request: Request, token: str = Depends(get_token)):
    return await forward_request("POST", f"{AUTH_SERVICE}/auth/admin/register",
                                 request=request, json_data=data.model_dump(), token=token)

@app.get("/auth/admin/users")
async def list_users(request: Request, token: str = Depends(get_token)):
    return await forward_request("GET", f"{AUTH_SERVICE}/auth/admin/users", request=request, token=token)

@app.patch("/auth/admin/users/{user_id}/role")
async def set_user_role(user_id: int, body: PromoteUser, request: Request, token: str = Depends(get_token)):
    return await forward_request("PATCH", f"{AUTH_SERVICE}/auth/admin/users/{user_id}/role",
                                 request=request, json_data=body.model_dump(), token=token)

@app.delete("/auth/admin/users/{user_id}")
async def delete_user(user_id: int, request: Request, token: str = Depends(get_token)):
    return await forward_request("DELETE", f"{AUTH_SERVICE}/auth/admin/users/{user_id}",
                                 request=request, token=token)
