from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base

# from flask_sqlalchemy import DeclarativeBase
from sqlalchemy.orm import session, sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:J211908a@localhost:5432/My_database"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DBContext:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, et, ev, traceback):
        self.db.close()
