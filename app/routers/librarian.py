from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..services.librarian import LibrarianService
from ..utility.exception import NotFoundException, InvalidPassword, ForbiddenError
from database.database import SessionLocal
from ..routers.auth import get_current_librarian

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
    name: str
    writer: str
    type: str
    subject: Optional[str]

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
async def get_all_books(librarian: librarian_dependency, db: db_dependency):
    try:
        check_librarian(librarian)
        librarian_service = LibrarianService(db)
        books = librarian_service.get_all_books()
        return books
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@router.post('/book/add')
async def add_book(librarian: librarian_dependency, db: db_dependency, book: BookRequest):
    try:
        check_librarian(librarian)
        librarian_service = LibrarianService(db)
        message = librarian_service.add_book(librarian, book.name, book.writer, book.type, book.subject)
        return {"message": message}
    except InvalidPassword as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.delete('/book/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, librarian: librarian_dependency, db: db_dependency):
    try:
        check_librarian(librarian)
        librarian_service = LibrarianService(db)
        librarian_service.delete_book(librarian, book_id)
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

def check_librarian(librarian: librarian_dependency) -> bool:
    if librarian is None:
        raise ForbiddenError()
    return True