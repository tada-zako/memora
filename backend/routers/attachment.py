from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import shutil
from pathlib import Path

from model import User, Event, EventAttachment
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
    event_id: int
    user_id: int
    description: Optional[str] = None

class AttachmentResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    url: str
    description: Optional[str] = None
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
    
    # Return relative URL
    return f"/uploads/{unique_filename}"

# Upload image/file attachment
@router.post("/upload/", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    event_id: int = Form(...),
    user_id: int = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file attachment for an event
    """
    # Validate file
    validate_file(file)
    
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Note: In a real application, you might want to check permissions here
    # For now, we allow any user to add attachments to any event
    
    try:
        # Save file
        file_url = save_file(file)
        
        # Create attachment record
        db_attachment = EventAttachment(
            event_id=event_id,
            user_id=user_id,
            url=file_url,
            description=description
        )
        
        db.add(db_attachment)
        db.commit()
        db.refresh(db_attachment)
        
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

# Get all attachments for an event
@router.get("/event/{event_id}", response_model=List[AttachmentResponse])
async def get_event_attachments(event_id: int, db: Session = Depends(get_db)):
    """
    Get all attachments for a specific event
    """
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    attachments = db.query(EventAttachment).filter(EventAttachment.event_id == event_id).all()
    return attachments

# Get attachment by ID
@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """
    Get a specific attachment by ID
    """
    attachment = db.query(EventAttachment).filter(EventAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id {attachment_id} not found"
        )
    return attachment

# Delete attachment
@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """
    Delete an attachment by ID
    """
    attachment = db.query(EventAttachment).filter(EventAttachment.id == attachment_id).first()
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
    db.delete(attachment)
    db.commit()
    
    return None
