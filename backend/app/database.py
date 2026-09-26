from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Use PostgreSQL if provided via environment variable, otherwise fallback to local SQLite for zero-setup demo
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./skillsetu.db")

# SQLite needs connect_args, PostgreSQL does not
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

def get_db():
    """Dependency to get database session for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()