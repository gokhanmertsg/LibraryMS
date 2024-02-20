from datetime import timedelta, datetime
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database.database import SessionLocal
from database.models.models import Librarian, Student
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from ..utility.exception import *
from dotenv import load_dotenv
import os

router: APIRouter = APIRouter(
    prefix='/auth',
    tags=['auth']
)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY: str = 'ffc512b54e2c73a276ea377d43361ab3a677e4845c8b0854bcaba180e530d9c0'
ALGORITHM: str = 'HS256'

db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl = 'auth/token')

class LibrarianRequest(BaseModel):
    """
    Librarian Authentication Request BaseModel.
    username: str
    password: str
    """
    username: str
    password: str

class StudentRequest(BaseModel):
    """
    Student Creation Request BaseModel.
    name: str
    department: str
    """
    name: str
    department: str
    
class Token(BaseModel):
    """
    JWT Token type BaseModel.
    access_token: str
    token_type: str
    """
    access_token: str
    token_type: str


def get_librarion_from_db( db: db_dependency, username: str) -> Librarian:
    librarian = db.query(Librarian).filter(Librarian.username == username).first()
    if not librarian:
        raise NotFoundException("Librarian not found.")
    return librarian

def check_password(password: str, hashed_password: str) -> bool:
    if not bcrypt_context.verify(password, hashed_password):
        raise InvalidPassword("Invalid password.")
    return True

def authenticate_librarian(username: str, password: str, db: db_dependency) -> Librarian:
    librarian = get_librarion_from_db(db, username)
    check_password(password, librarian.hashed_password)
    return librarian

def create_access_token(username: str, librarian_id: int, expires_delta: timedelta) -> str:
    encode: dict[str, str|int] = {'sub': username, 'id': librarian_id}
    expires: datetime = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_librarian(token: Annotated[str, Depends(oauth2_bearer)]) -> dict[str, str|int]:
    try:
        payload: dict[str,any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        librarian_id: int = payload.get('id')
        if username is None or librarian_id is None:
            raise JWTError
        return {'username': username, 'id': librarian_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate librarian.')

@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_librarian(db: db_dependency, create_librarian_request: LibrarianRequest):
    create_user_model: Librarian = Librarian(
        username = create_librarian_request.username,
        hashed_password = bcrypt_context.hash(create_librarian_request.password),
    )
    
    db.add(create_user_model)
    db.commit()

@router.post("/student", status_code=status.HTTP_201_CREATED)
async def create_student(db: db_dependency, create_student_request: StudentRequest) -> dict[str, int]:
    student: Student = Student(
        name = create_student_request.name,
        department = create_student_request.department,
    )
    
    db.add(student)
    db.commit()
    db.refresh(student)

    if student.student_id:
        return {"student_id" : student.student_id}
    else:
        raise HTTPException(status_code=500, detail="Öğrenci oluşturulamadı.")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                                      db: db_dependency) -> Token:
    librarian: Librarian = authenticate_librarian(form_data.username, form_data.password, db)
    if not librarian:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate librarian.')
    token: str = create_access_token(librarian.username, librarian.librarian_id, timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'bearer'
    }