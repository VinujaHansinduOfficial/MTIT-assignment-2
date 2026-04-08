from fastapi import FastAPI
from app.routers import enrollment
from app.database import initialize_database

app = FastAPI()


@app.on_event("startup")
def startup():
    initialize_database()


app.include_router(
    enrollment.router,
    prefix="/enrollments",
    tags=["Enrollment Service"]
)


@app.get("/")
def root():
    return {"message": "Enrollment Service is running"}