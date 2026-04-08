from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.database import engine, Base
from app.routers import course_router, subject_router, auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready.")
    except OperationalError as e:
        print(
            f"⚠️ Could not connect to the database at startup: {e}\n"
            "Make sure MySQL is running and DATABASE_URL is correct.\n"
            "The app will still start, but DB operations will fail until the connection is available."
        )
    yield


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
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
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

