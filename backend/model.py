from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from db import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)

    # Relationship to collections
    collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Collection(Base):
    __tablename__ = 'collections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category = Column(String(50), nullable=False)
    tags = Column(String(255), nullable=True) # splited by comma
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="collections")

    def __repr__(self):
        return f"<Collection(id={self.id}, user_id={self.user_id}, category='{self.category}...')>"


class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Attachment(id={self.id}, collection_id={self.collection_id}, url='{self.url}')>"

