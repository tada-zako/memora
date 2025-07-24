from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./memora.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    # SQLite specific settings
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base for declarative models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    This function creates a new SQLAlchemy SessionLocal that will be used in a single request,
    and then close it once the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables in the database.
    This should be called when the application starts.
    """
    from model import Base  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Drop all tables in the database.
    Use with caution - this will delete all data!
    """
    from model import Base  # Import here to avoid circular imports
    Base.metadata.drop_all(bind=engine)

def reset_database():
    """
    Drop and recreate all tables.
    Use with caution - this will delete all data!
    """
    drop_tables()
    create_tables()
