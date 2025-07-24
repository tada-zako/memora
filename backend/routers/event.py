from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from model import User, Event
from db import get_db

# Create router instance
router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response
class EventCreate(BaseModel):
    user_id: int
    description: str
    metadata: Optional[dict] = None

class EventUpdate(BaseModel):
    description: Optional[str] = None
    metadata: Optional[dict] = None

class EventResponse(BaseModel):
    id: int
    user_id: int
    description: str
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Create Event
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Create a new event
    """
    # Check if user exists
    user = db.query(User).filter(User.id == event.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {event.user_id} not found"
        )
    
    db_event = Event(
        user_id=event.user_id,
        description=event.description,
        metadata=event.metadata
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# Get all events
@router.get("/", response_model=List[EventResponse])
async def get_events(
    skip: int = 0, 
    limit: int = 100, 
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all events with optional filtering by user_id
    """
    query = db.query(Event)
    
    if user_id:
        query = query.filter(Event.user_id == user_id)
    
    events = query.order_by(desc(Event.created_at)).offset(skip).limit(limit).all()
    return events

# Get event by ID
@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Get a specific event by ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return event

# Update event
@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int, 
    event_update: EventUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing event
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    # Update only provided fields
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event

# Delete event
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """
    Delete an event by ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    db.delete(event)
    db.commit()
    return None

# Additional router for user-specific events
user_events_router = APIRouter(
    prefix="/users",
    tags=["users", "events"],
    responses={404: {"description": "Not found"}},
)

# Get events by user
@user_events_router.get("/{user_id}/events/", response_model=List[EventResponse])
async def get_user_events(
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all events for a specific user
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    events = db.query(Event).filter(Event.user_id == user_id)\
        .order_by(desc(Event.created_at))\
        .offset(skip).limit(limit).all()
    return events
