from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from app import models
from app.database import engine
from app.routers import enrollment, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready.")
    except OperationalError as e:
        print(
            f"⚠️ Could not connect to the database at startup: {e}\n"
            "Make sure MySQL is running and DATABASE_URL is correct.\n"
            "The app will still start, but DB operations will fail until the connection is available."
        )
    yield


app = FastAPI(title="Enrollment Service", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(
    enrollment.router,
    prefix="/enrollments",
    tags=["Enrollment Service"],
)


@app.get("/")
def root():
    return {"message": "Enrollment Service is running"}
