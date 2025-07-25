from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import shutil
from pathlib import Path

from model import User, Collection, Attachment
from db import get_db

# Create router instance
router = APIRouter(
    prefix="/attachments",
    tags=["attachments"],
    responses={404: {"description": "Not found"}},
)

# Configuration for file uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

# Pydantic models
class AttachmentCreate(BaseModel):
    collection_id: int
    user_id: int
    description: Optional[str] = None

class AttachmentResponse(BaseModel):
    id: int
    collection_id: int
    user_id: int
    url: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AttachmentUpdate(BaseModel):
    description: Optional[str] = None

# Helper function to validate file
def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected"
        )
    
    # Check file extension
    file_ext = Path(str(file.filename)).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

# Helper function to save file
def save_file(file: UploadFile) -> str:
    """Save uploaded file and return URL"""
    # Generate unique filename
    file_ext = Path(str(file.filename)).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return unique_filename

# Upload attachment endpoint
@router.post("/upload/", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    collection_id: int = Form(...),
    user_id: int = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file attachment for a collection
    """
    # Validate file
    validate_file(file)
    
    # Check if collection exists
    collection_query = select(Collection).where(Collection.id == collection_id)
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection with id {collection_id} not found"
        )
    
    # Check if user exists
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    try:
        # Save file
        file_url = save_file(file)
        
        # Create attachment record
        db_attachment = Attachment(
            collection_id=collection_id,
            user_id=user_id,
            url=file_url,
            description=description
        )
        
        db.add(db_attachment)
        await db.commit()
        await db.refresh(db_attachment)
        
        return db_attachment
        
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_url' in locals():
            file_path = UPLOAD_DIR / Path(file_url).name
            if file_path.exists():
                file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

# Get all attachments for a collection
@router.get("/collection/{collection_id}", response_model=List[AttachmentResponse])
async def get_collection_attachments(collection_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all attachments for a specific collection
    """
    # Check if collection exists
    collection_query = select(Collection).where(Collection.id == collection_id)
    collection_result = await db.execute(collection_query)
    collection = collection_result.scalar_one_or_none()
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection with id {collection_id} not found"
        )
    
    attachments_query = select(Attachment).where(Attachment.collection_id == collection_id)
    attachments_result = await db.execute(attachments_query)
    attachments = attachments_result.scalars().all()
    return attachments

# Get attachment by ID
@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(attachment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific attachment by ID
    """
    attachment_query = select(Attachment).where(Attachment.id == attachment_id)
    attachment_result = await db.execute(attachment_query)
    attachment = attachment_result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id {attachment_id} not found"
        )
    return attachment

# Delete attachment
@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(attachment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete an attachment by ID
    """
    attachment_query = select(Attachment).where(Attachment.id == attachment_id)
    attachment_result = await db.execute(attachment_query)
    attachment = attachment_result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id {attachment_id} not found"
        )
    
    # Delete file from filesystem
    try:
        file_path = UPLOAD_DIR / Path(str(attachment.url)).name
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass  # Continue even if file deletion fails
    
    # Delete database record
    await db.delete(attachment)
    await db.commit()
    
    return None
