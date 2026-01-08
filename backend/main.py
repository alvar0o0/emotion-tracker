from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

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
def log_emotion(emotion: Emotion, db: "Session" = Depends(get_db)):
    db_emotion = EmotionLog(emotion=emotion.emotion, level=emotion.level)
    db.add(db_emotion)
    db.commit()
    db.refresh(db_emotion)
    return db_emotion
