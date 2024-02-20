from datetime import timedelta, datetime
import os
from typing import Optional
from dotenv import load_dotenv

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database.models.models import BookType, Librarian, Student
from ..utility.exception import NotFoundException, InvalidPassword


load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM")

bcrypt_context: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')

class AuthService:
    
    def __init__(self, db: Session):
        self.db = db
        

    def initialize_book_types(self):
        type1 = BookType(type_name='reading')
        type2 = BookType(type_name='school')
        self.db.add(type1)
        self.db.add(type2)
        self.db.commit()

    def create_librarian(self, username: str, password: str):
        librarian = self.db.query(Librarian).filter(Librarian.username == username).first()

        if librarian is not None:
            raise HTTPException(status_code=400, detail='Librarian already exists.')

        create_user_model = Librarian(
            username=username,
            hashed_password=bcrypt_context.hash(password),
        )

        self.db.add(create_user_model)
        self.db.commit()

    def create_student(self, name: str, department: str) -> int:
        student = Student(
            name=name,
            department=department,
        )

        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)

        if student.student_id:
            return student.student_id
        else:
            raise HTTPException(status_code=500, detail="Student could not be created.")

    def authenticate_librarian(self, username: str, password: str) -> Librarian:
        librarian = self.get_librarian_from_db(username)
        self.check_password(password, librarian.hashed_password)
        return librarian

    def create_access_token(self, username: str, librarian_id: int, expires_delta: Optional[timedelta] = None) -> str:
        encode = {'sub': username, 'id': librarian_id}
        if expires_delta:
            expires = datetime.utcnow() + expires_delta
            encode.update({'exp': expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    def get_librarian_from_db(self, username: str) -> Librarian:
        librarian = self.db.query(Librarian).filter(Librarian.username == username).first()
        if not librarian:
            raise NotFoundException("Librarian not found.")
        return librarian

    def check_password(self, password: str, hashed_password: str) -> bool:
        if not bcrypt_context.verify(password, hashed_password):
            raise InvalidPassword("Invalid password.")
        return True

    def login_for_access_token(self, form_data: OAuth2PasswordRequestForm) -> dict:
        librarian = self.authenticate_librarian(form_data.username, form_data.password)
        token = self.create_access_token(librarian.username, librarian.librarian_id, timedelta(minutes=20))
        return {
            'access_token': token,
            'token_type': 'bearer'
        }
