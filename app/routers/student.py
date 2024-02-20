import datetime
from typing import Annotated, List
from pydantic import BaseModel
from sqlalchemy import Date, func, update
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from database.models.models import Book, BookSubject, BorrowedBooks, Student
from database.database import SessionLocal
from starlette import status
from ..utility.utils import BookTypeEnum

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

def get_student(db:db_dependency, student_id: int) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student

@router.get('/books/me')
async def get_student_books(db:db_dependency, student_id: int) -> BookResponse:
    student: Student= get_student(db, student_id)    
    
    books: List[Book] = db.query(Book).join(BorrowedBooks).filter(BorrowedBooks.student_id == student_id).filter(BorrowedBooks.is_returned == False).all()
    books_with_subjects: List[dict] = books_with_subject(db, books)
    
    return BookResponse(student_name=student.name, books=books_with_subjects)

@router.get('/books')
async def get_available_books(db:db_dependency, student_id: int):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Student not found.")
    
    borrowed_books : List[BorrowedBooks]= db.query(BorrowedBooks).filter(BorrowedBooks.is_returned == False).all()
    borrowed_book_ids: List[int] = [book.book_id for book in borrowed_books]

    available_books: List[Book] = db.query(Book).filter(~(Book.book_id.in_(borrowed_book_ids))).all()
    available_books_with_subject: List[dict] = books_with_subject(db, available_books)
    
    return BookResponse(student_name=student.name, books=available_books_with_subject)

@router.get('/{book_id}')
async def get_book(db:db_dependency, book_id:int, student_id:int):
    student: Student = get_student(db, student_id)

    book: Book = db.query(Book).filter(Book.book_id == book_id).first()
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book does not exist.")
    book_dict = book_subject_append(db, book)
    return book_dict

@router.get('/borrow/{book_id}')
async def borrow_book(db:db_dependency, book_id: int, student_id: int) -> dict[str, str]:
    student: Student = get_student(db,student_id)
    book: Student = db.query(Book).filter(Book.book_id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if db.query(BorrowedBooks).filter(
        BorrowedBooks.book_id == book_id,
        BorrowedBooks.is_returned == False
    ).first():
        raise HTTPException(status_code=400, detail="Book already borrowed")

    borrowed_book: BorrowedBooks = BorrowedBooks(student_id=student_id, book_id=book_id, borrow_date=func.now(), is_returned = False)
    db.add(borrowed_book)
    db.commit()

    return {"message": "Book borrowed successfully"}

@router.put('/return/{book_id}')
async def return_book(db: db_dependency, book_id: int, student_id: int) -> dict[str, str]:
    student: Student = get_student(db, student_id)

    borrowed_book: BorrowedBooks = db.query(BorrowedBooks).filter(
        BorrowedBooks.book_id == book_id,
        BorrowedBooks.student_id == student.student_id,
        BorrowedBooks.is_returned == False
    ).first()

    if not borrowed_book:
        raise HTTPException(status_code=404, detail="Borrowed book not found")

    return_date: Date= func.now()
    db.execute(
        update(BorrowedBooks)
        .where(BorrowedBooks.borrow_id == borrowed_book.borrow_id)
        .values(return_date=return_date, is_returned = True)
    )
    db.commit()

    return {"message": "Book returned successfully"}


def books_with_subject(db:db_dependency, books) -> List[dict]:
    books_with_subject: List[dict] = []
    for book in books:
        books_with_subject.append(book_subject_append(db,book))
    return books_with_subject

def book_subject_append(db:db_dependency, book: Book) -> dict:
    book_dict: dict = {
            'book_id': book.book_id,
            'writer': book.writer,
            'name': book.name,
            'type_id': book.type_id,
        }

    if book.type_id == BookTypeEnum.SCHOOL.value:
        school_book: BookSubject = db.query(BookSubject).filter(BookSubject.book_id == book.book_id).first()
        if school_book and school_book.subject:
            book_dict['subject'] = school_book.subject
    return book_dict        
    
    

