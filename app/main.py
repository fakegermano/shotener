import os
import uvicorn
import string
from datetime import datetime, timedelta
from random import choices
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./prod.db")

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DbUrl(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    key = Column(String, index=True, unique=True)
    expires = Column(DateTime, nullable=True)

class UrlBase(BaseModel):
    url: str

class UrlCreate(UrlBase):
    pass


class Url(UrlBase):
    id: int
    key: str
    expires: datetime

    class Config:
        orm_mode = True


def get_url(db: Session, key: str) -> DbUrl:
    return db.query(DbUrl).filter(DbUrl.key == key).first()

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

app = FastAPI(title="URL shortener with FastAPI")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/{key}", response_class=RedirectResponse, status_code=302, responses={
    404: {"description": "key for url not found"},
})
async def expander(key: str, db: Session=Depends(get_db)):
    url = get_url(db, key)
    if not url:
        return HTTPException(status_code=404, detail="URL for key not found")
    return "https://" + url.url

@app.post("/", response_class=Response, responses={
    200: {"description": "Creates key from url"},
})
async def shortener(url: UrlCreate, request: Request, db: Session=Depends(get_db)):
    db_url = create_url(db, url.url)
    return Response(status_code=200, 
                    content=(
                        request.url.scheme + "://" + 
                        request.url.hostname + 
                        ((":" + str(request.url.port)) if request.url.port else "") + "/" + 
                        db_url.key))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)