from typing import Optional, List

from sqlalchemy.orm import Session

from database.models.models import Book, BookType, BookSubject
from ..utility.exception import NotFoundException, InvalidPassword, ForbiddenError
from ..utility.utils import BookTypeEnum

class LibrarianService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_books(self):
        try:
            books = self.db.query(Book).all()
            books_with_subjects = self.books_with_subject(books)
            return books_with_subjects
        except Exception as e:
            raise NotFoundException("Books not found") from e

    def add_book(self, librarian: dict, book_name: str, writer: str, book_type: str, subject: Optional[str]):
        try:
            type = self.db.query(BookType).filter(BookType.type_name == book_type.lower()).first()

            if not type:
                book_types = self.db.query(BookType).all()
                book_types_names = [book_type.type_name for book_type in book_types]
                raise NotFoundException(f"Book Type not found. Current book types: {book_types_names}")

            new_book = Book(writer=writer, name=book_name, type_id=type.type_id, type=type)
            self.db.add(new_book)
            self.db.commit()

            self.db.refresh(new_book)

            if type.type_name == 'school':
                subject_book = BookSubject(book_id=new_book.book_id, subject=subject)
                self.db.add(subject_book)
                self.db.commit()
            return {"message": "Book added successfully"}
        except Exception as e:
            raise InvalidPassword("Invalid password") from e

    def delete_book(self, librarian: dict, book_id: int):
        try:
            school_book: BookSubject = self.db.query(BookSubject).filter(BookSubject.book_id == book_id).first()
            if school_book:
                self.db.query(BookSubject).filter(BookSubject.book_id == book_id).delete()
                self.db.commit()

            book_model: Book = self.db.query(Book).filter(Book.book_id == book_id).first()
            if book_model is None:
                raise NotFoundException('Book does not exist.')

            self.db.query(Book).filter(Book.book_id == book_id).delete()
            self.db.commit()
        except Exception as e:
            print(e)
            raise ForbiddenError("Forbidden") from e

    def books_with_subject(self, books) -> List[dict]:
        books_with_subject: List[dict] = []
        for book in books:
            books_with_subject.append(self.book_subject_append(book))
        return books_with_subject

    def book_subject_append(self, book: Book) -> dict:
        book_dict: dict = {
            'book_id': book.book_id,
            'writer': book.writer,
            'name': book.name,
            'type_id': book.type_id,
        }

        if book.type_id == BookTypeEnum.SCHOOL.value:
            school_book: BookSubject = self.db.query(BookSubject).filter(BookSubject.book_id == book.book_id).first()
            if school_book and school_book.subject:
                book_dict['subject'] = school_book.subject
        return book_dict
