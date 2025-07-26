import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from db import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_attachment_id = Column(String(36), ForeignKey('attachments.attachment_id'), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to collections
    collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")
    avatar = relationship("Attachment", foreign_keys=[avatar_attachment_id])

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

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
    is_shared = Column(Boolean, default=False, nullable=False)  # 是否分享到社区
    shared_description = Column(Text, nullable=True)  # 分享时的描述
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="collections")
    category = relationship("Category")
    details = relationship("CollectionDetail", back_populates="collection", cascade="all, delete-orphan")
    likes = relationship("CollectionLike", back_populates="collection", cascade="all, delete-orphan")
    comments = relationship("CollectionComment", back_populates="collection", cascade="all, delete-orphan")

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
    attachment_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Attachment(attachment_id={self.attachment_id}, url='{self.url}')>"


class CollectionAttachment(Base):
    __tablename__ = 'collection_attachments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    attachment_id = Column(String(36), ForeignKey('attachments.attachment_id'), nullable=False)

    def __repr__(self):
        return f"<CollectionAttachment(attachment_id={self.id}, collection_id={self.collection_id}, attachment_id={self.attachment_id})>"


class CollectionLike(Base):
    __tablename__ = 'collection_likes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="likes")
    user = relationship("User")

    def __repr__(self):
        return f"<CollectionLike(id={self.id}, collection_id={self.collection_id}, user_id={self.user_id})>"


class CollectionComment(Base):
    __tablename__ = 'collection_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="comments")
    user = relationship("User")

    def __repr__(self):
        return f"<CollectionComment(id={self.id}, collection_id={self.collection_id}, user_id={self.user_id})>"
