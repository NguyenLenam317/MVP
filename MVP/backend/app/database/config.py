from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/alt_data"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_db_settings():
    return DatabaseSettings()

settings = get_db_settings()

# SQLAlchemy configuration
engine = create_engine(settings.DATABASE_URL, pool_size=20, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for declarative models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
