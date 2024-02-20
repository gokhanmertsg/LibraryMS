from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Date, func, update

from database.models.models import BookSubject

from ..utility.exception import NotFoundException
from database.models.models import Book, BorrowedBooks, Student
from ..utility.utils import BookTypeEnum

class StudentService:
    def __init__(self, db: Session):
        self.db = db

    def get_student_books(self, student_id: int) -> dict:
        student = self.get_student(student_id)
        books = self.get_student_borrowed_books(student_id)
        books_with_subjects = self.books_with_subject(books)
        return {"student_name": student.name, "books": books_with_subjects}

    def get_available_books(self, student_id: int) -> dict:
        student = self.get_student(student_id)
        borrowed_books = self.get_student_borrowed_books(student_id)
        borrowed_book_ids = [book.book_id for book in borrowed_books]
        available_books = self.db.query(Book).filter(~(Book.book_id.in_(borrowed_book_ids))).all()
        available_books_with_subject = self.books_with_subject(available_books)
        return {"student_name": student.name, "books": available_books_with_subject}

    def get_book(self, student_id: int, book_id: int) -> dict:
        student = self.get_student(student_id)
        book = self.db.query(Book).filter(Book.book_id == book_id).first()
        if book is None:
            raise NotFoundException("Book does not exist.")
        book_dict = self.book_subject_append(book)
        return book_dict

    def borrow_book(self, student_id: int, book_id: int) -> str:
        student = self.get_student(student_id)
        book = self.db.query(Book).filter(Book.book_id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        if self.db.query(BorrowedBooks).filter(
            BorrowedBooks.book_id == book_id,
            BorrowedBooks.is_returned == False
        ).first():
            raise HTTPException(status_code=400, detail="Book already borrowed")

        borrowed_book = BorrowedBooks(student_id=student_id, book_id=book_id, borrow_date=func.now(), is_returned=False)
        self.db.add(borrowed_book)
        self.db.commit()

        return "Book borrowed successfully"

    def return_book(self, student_id: int, book_id: int) -> str:
        student = self.get_student(student_id)

        borrowed_book = self.db.query(BorrowedBooks).filter(
            BorrowedBooks.book_id == book_id,
            BorrowedBooks.student_id == student.student_id,
            BorrowedBooks.is_returned == False
        ).first()

        if not borrowed_book:
            raise HTTPException(status_code=404, detail="Borrowed book not found")

        return_date = func.now()
        self.db.execute(
            update(BorrowedBooks)
            .where(BorrowedBooks.borrow_id == borrowed_book.borrow_id)
            .values(return_date=return_date, is_returned=True)
        )
        self.db.commit()

        return "Book returned successfully"

    def get_student(self, student_id: int) -> Student:
        student = self.db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise NotFoundException("Student not found.")
        return student

    def get_student_borrowed_books(self, student_id: int) -> List[Book]:
        return (
            self.db.query(Book)
            .join(BorrowedBooks)
            .filter(BorrowedBooks.student_id == student_id)
            .filter(BorrowedBooks.is_returned == False)
            .all()
        )

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
