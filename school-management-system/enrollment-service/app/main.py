from fastapi import FastAPI
from app.routers import enrollment

app = FastAPI()

app.include_router(
    enrollment.router,
    prefix="/enrollments",
    tags=["Enrollment Service"]
)