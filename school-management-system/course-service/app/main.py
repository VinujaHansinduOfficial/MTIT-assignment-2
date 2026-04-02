from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import course_router, subject_router

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Course & Subject Management Service",
    description=(
        "Microservice responsible for managing **Courses** and **Subjects** "
        "in the School Management System.\n\n"
        "## Endpoints\n"
        "- **Courses** – Create, Read, Update, Delete courses\n"
        "- **Subjects** – Create, Read, Update, Delete subjects\n"
        "- **Assign Teacher** – Link a teacher (from Teacher Service) to a subject\n"
        "- **Filter** – View all subjects belonging to a specific course\n\n"
        "Part of **IT4020 Assignment 2** – Microservices Architecture @ SLIIT"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(course_router.router)
app.include_router(subject_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "service": "Course & Subject Management Service",
        "status": "running ✅",
        "port": 8003,
        "docs": "/docs",
        "endpoints": {
            "courses": "/courses",
            "subjects": "/subjects",
        }
    }
