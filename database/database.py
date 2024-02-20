import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

database_url: str = os.getenv("DATABASE_URL", default='postgresql://postgres:test1234@localhost:5432/libraryms_db')

engine: Engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

