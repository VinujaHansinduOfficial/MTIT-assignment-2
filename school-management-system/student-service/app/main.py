from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import student


app = FastAPI(title="Student Service")

models.Base.metadata.create_all(bind=engine)

app.include_router(student.router)
