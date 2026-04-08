from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from .database import Base, engine
from .routers import teacher, auth


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
    title="Teacher Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(teacher.router)


@app.get("/")
def root():
    return {"message": "Teacher Service is running"}