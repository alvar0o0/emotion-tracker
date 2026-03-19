import os
import sys
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, validator
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import datetime
import logging

# Ensure the root directory is on the path so we can import shared
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.constants import get_valid_emotions

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./emotions.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id = Column(Integer, primary_key=True, index=True)
    emotion = Column(String, index=True)
    level = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic model for request body
class Emotion(BaseModel):
    emotion: str
    level: int

    @validator('emotion')
    def emotion_must_be_valid(cls, v):
        if v not in get_valid_emotions():
            raise ValueError(f"Emotion must be one of {get_valid_emotions()}")
        return v

    @validator('level')
    def level_must_be_valid(cls, v):
        if not (1 <= v <= 5):
            raise ValueError("Level must be between 1 and 5")
        return v

class EmotionResponse(Emotion):
    id: int
    timestamp: datetime.datetime
    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/log")
def log_emotion(emotion: Emotion, db: Session = Depends(get_db)):
    logger.info("Logging emotion: %s with level %d", emotion.emotion, emotion.level)
    db_emotion = EmotionLog(emotion=emotion.emotion, level=emotion.level)
    db.add(db_emotion)
    db.commit()
    db.refresh(db_emotion)
    logger.info("Emotion logged with ID: %d", db_emotion.id)
    return db_emotion

@app.get("/logs", response_model=List[EmotionResponse])
def get_logs(db: Session = Depends(get_db)):
    logger.info("Fetching all emotion logs")
    logs = db.query(EmotionLog).all()
    logger.info("Fetched %d logs", len(logs))
    return logs
