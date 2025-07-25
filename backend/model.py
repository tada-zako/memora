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

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(50), unique=True, nullable=False)
    emoji = Column(String(10), nullable=True)  # Optional emoji for category

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
    

class Collection(Base):
    __tablename__ = 'collections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    tags = Column(String(255), nullable=True) # splited by comma
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="collections")
    category = relationship("Category")
    details = relationship("CollectionDetail", back_populates="collection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Collection(id={self.id}, user_id={self.user_id}, category='{self.category}...')>"


class CollectionDetail(Base):
    __tablename__ = 'collection_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    collection = relationship("Collection", back_populates="details")

    def __repr__(self):
        return f"<CollectionDetail(id={self.id}, collection_id={self.collection_id}, key='{self.key}')>"


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

