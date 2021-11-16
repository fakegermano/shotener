import uvicorn
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, Depends
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)

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


def get_url_by_url(db: Session, url: str) -> DbUrl:
    return db.query(Url).filter(Url.url == url).first()

def get_url_by_key(db: Session, key: str) -> DbUrl:
    return db.query(Url).filter(Url.key == key).first()

def create_url(db: Session, url: str) -> DbUrl:
    key = str(uuid4()) # TODO change here to something within 5-10 characters and validate
    expires = datetime.now() + timedelta(hours=1)
    db_url = DbUrl(url=url, key=key, expires=expires)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
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
async def index(url: str, db: Session=Depends(get_db)):
    db_url = create_url(db, url)
    return db_url

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)