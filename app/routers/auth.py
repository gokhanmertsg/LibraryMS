from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from database.database import SessionLocal
from ..services.auth import SECRET_KEY,ALGORITHM, AuthService

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

auth_service = AuthService(SessionLocal())
db_dependency = Annotated[Session, Depends(get_db)]
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

@router.get("/initialize")
async def initialize_book_types(db:   db_dependency):
    auth_service.initialize_book_types()
    return {"message": "Book types initialized successfully"}

@router.post("/auth")
async def create_librarian(create_librarian_request: LibrarianRequest, db:   db_dependency):
    auth_service.create_librarian(create_librarian_request.username, create_librarian_request.password)
    return {"message": "Librarian created successfully"}

@router.post("/student")
async def create_student(create_student_request: StudentRequest, db:   db_dependency):
    student_id = auth_service.create_student(create_student_request['name'], create_student_request['department'])
    return {"student_id": student_id}

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:   db_dependency):
    token_response = auth_service.login_for_access_token(form_data)
    return token_response
