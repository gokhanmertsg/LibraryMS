from typing import Annotated
from fastapi import Depends
from pytest import Session
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

database_url: str = 'postgresql://postgres:test1234@localhost:5432/libraryms_db'

engine: Engine = create_engine(database_url)

SessionLocal: Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

