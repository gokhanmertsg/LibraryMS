from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import SessionLocal
from ..services.student import StudentService
from ..utility.exception import NotFoundException

router = APIRouter(
    prefix='/student',
    tags=['student']
)

class BookResponse(BaseModel):
    """
    Response BaseModel for Book requests.
    student_name: str
    books: list of dicts.
    """
    student_name: str
    books: List[dict]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get('/books/me')
async def get_student_books(student_id: int, db: db_dependency) -> BookResponse:
    try:
        student_service = StudentService(db)
        books = student_service.get_student_books(student_id)
        return books
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@router.get('/books')
async def get_available_books(student_id: int, db: db_dependency) -> BookResponse:
    try:
        student_service = StudentService(db)
        books = student_service.get_available_books(student_id)
        return books
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@router.get('/{book_id}')
async def get_book(db: db_dependency, book_id: int, student_id: int) -> dict:
    try:
        student_service = StudentService(db)
        book = student_service.get_book(student_id, book_id)
        return book
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@router.get('/borrow/{book_id}')
async def borrow_book(book_id: int, student_id: int, db: db_dependency) -> dict:
    try:
        student_service = StudentService(db)
        message = student_service.borrow_book(student_id, book_id)
        return {"message": message}
    except HTTPException as e:
        raise e

@router.put('/return/{book_id}')
async def return_book(book_id: int, student_id: int, db: db_dependency) -> dict:
    try:
        student_service = StudentService(db)
        message = student_service.return_book(student_id, book_id)
        return {"message": message}
    except HTTPException as e:
        raise e
