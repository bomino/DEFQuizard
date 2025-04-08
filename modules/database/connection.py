import os
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# Database file path
DATABASE_DIR = "data"
DATABASE_PATH = os.path.join(DATABASE_DIR, "forklift_training.db")

# Ensure data directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

# Create database engine
engine = sa.create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)

# Create tables if they don't exist
Base.metadata.create_all(engine)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_db_session():
    """
    Get a scoped database session
    
    Returns:
        sqlalchemy.orm.Session: Database session
    """
    return Session()

def close_db_session():
    """Close the current database session"""
    Session.remove()

def init_db():
    """Initialize the database schema"""
    Base.metadata.create_all(engine)