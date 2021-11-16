import uvicorn
import string
from uuid import uuid4
from datetime import datetime, timedelta
from random import choices
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel, HttpUrl

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DbUrl(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    key = Column(String, index=True, unique=True)
    expires = Column(DateTime, nullable=True)

class Url(BaseModel):
    id: int
    url: str
    key: str
    expires: datetime

    class Config:
        orm_mode = True


def get_url(db: Session, key: str) -> DbUrl:
    return db.query(Url).filter(Url.key == key).first()

key_characters = string.ascii_letters + string.digits

def create_url(db: Session, url: str) -> DbUrl:
    while True:
        try:
            key = "".join(choices(key_characters, k=8))
            expires = datetime.now() + timedelta(hours=1)
            db_url = DbUrl(url=url, key=key, expires=expires)
            db.add(db_url)
            db.commit()
        except IntegrityError:
            db.rollback()
        else:
            db.refresh(db_url)
            break
    return db_url


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/{url}")
async def shortener(url: str, request: Request, db: Session=Depends(get_db)) -> HttpUrl:
    db_url = create_url(db, url)
    return (
        request.url.scheme + "://" + 
        request.url.hostname + 
        ((":" + request.url.port) if request.url.port else "") + "/" + 
        db_url.key)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)