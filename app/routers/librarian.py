from typing import Annotated, List, Optional
from annotated_types import LowerCase
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Body, APIRouter, Depends, HTTPException, Path
from database.models.models import Book, BookSubject, BookType, Librarian
from database.database import engine, SessionLocal
from starlette import status
from ..routers import auth
from .auth import get_current_librarian
from ..utility.utils import BookStatusEnum, BookTypeEnum
from ..utility.exception import *

router: APIRouter = APIRouter(
    prefix='/librarian',
    tags=['librarian']
)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookRequest(BaseModel):
    """
    BaseModel for Request Type of Book Object.
    name: str
    writer: str
    type: str
    subject: Optional[str]
    """
    name:str
    writer:str
    type:str
    subject:Optional[str]
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Sensgreen",
                    "writer": "Gokhan Mert Gunes",
                    "type": "School, Reading etc.",
                    "subject": "Just for School Book Type.",
                }
            ]
        }
    }
 

db_dependency = Annotated[Session, Depends(get_db)]
librarian_dependency = Annotated[dict, Depends(get_current_librarian)]

@router.get('/books')
async def get_all_books(librarian:librarian_dependency, db:db_dependency):
    if librarian is None:
        raise HTTPException(status_code=401,detail="Unauthorized Access.")
    
    books = db.query(Book).all()
    books_with_subjects = books_with_subject(db, books)

    return books_with_subjects

@router.post('/book/add')
async def add_book(librarian:librarian_dependency, db:db_dependency, book:BookRequest) -> dict[str, str]:
    type = db.query(BookType).filter(BookType.type_name == book.type.lower()).first()

    if not type:
        book_types = db.query(BookType).all()
        book_types_names = [book_type.type_name for book_type in book_types]
        raise HTTPException(status_code=404, detail=f"Book Type not found. Current book types: {book_types_names}")

    new_book = Book(writer=book.writer, name=book.name, type_id= type.type_id, type=type)
    db.add(new_book)
    db.commit()

    db.refresh(new_book)

    if(type.type_name == 'school'):
        subject_book = BookSubject(book_id=new_book.book_id, subject=book.subject)
        db.add(subject_book)
        db.commit()
    return {"message": "Book added successfully"}


@router.delete('/book/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(librarian:librarian_dependency, db:db_dependency, book_id:int):   
    if librarian is None:
        raise HTTPException(status_code=401,detail="Unauthorized Access.")
    book_model: Book = db.query(Book).filter(Book.book_id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404, detail='Book does not exist.')
    db.query(Book).filter(Book.book_id==book_id).delete()
    db.commit()


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