from fastapi import FastAPI

from database.models.models import Base
from database.database import engine
from .routers import student, auth, librarian

app: FastAPI = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(librarian.router)
app.include_router(student.router)
