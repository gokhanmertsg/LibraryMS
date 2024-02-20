from ..database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

class Librarian(Base):
    """
    librarian_id: Integer, PK, auto_generated
    username: String
    hashed_password: String
    """
    __tablename__ = 'librarians'
    librarian_id = Column(Integer, primary_key=True)
    username = Column(String)
    hashed_password = Column(String)

class Student(Base):
    """
    student_id: Integer, PK, auto_generated
    name: String
    department: String
    """
    __tablename__ = 'students'
    student_id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)

class Book(Base):
    """
    book_id: Integer, PK, auto_generated
    writer: String
    name: String
    type_id: Integer, FK, BookTypes.type_id
    """
    __tablename__ = 'books'
    book_id = Column(Integer, primary_key=True)
    writer = Column(String)
    name = Column(String)
    type_id = Column(Integer, ForeignKey('book_types.type_id'))
    type = relationship("BookType", back_populates="books")


class BookType(Base):
    """
    type_id: Integer, PK, auto_generated
    type_name: String
    """
    __tablename__ = 'book_types'
    type_id = Column(Integer, primary_key=True)
    type_name = Column(String)
    books = relationship("Book", back_populates="type")
    
class BookSubject(Base):
    """
    book_id: Integer
    subject: String
    """
    __tablename__ = 'school_books'
    subject_id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'))
    subject = Column(String)

class BorrowedBooks(Base):
    """
    borrow_id: Integer, PK, auto_generated
    student_id: Integer, FK, Student.student_id
    book_id: Integer, FK, Book.book_id
    borrow_date: Date
    return_date: Date
    is_returned: Boolean
    """
    __tablename__ = 'borrowed_books'
    borrow_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.student_id'))
    book_id = Column(Integer, ForeignKey('books.book_id'))
    borrow_date = Column(Date)
    return_date = Column(Date)
    is_returned = Column(Boolean, default=False)

