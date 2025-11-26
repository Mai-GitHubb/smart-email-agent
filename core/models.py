"""
Data models for the Smart Email Agent.

Defines the core data structures: Email, Task, Event, and Reminder.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Email(BaseModel):
    """Represents an email message."""
    id: str
    sender: str
    sender_name: str
    subject: str
    body: str
    timestamp: datetime
    labels: List[str] = Field(default_factory=list)
    has_attachments: bool = False
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    category: Optional[str] = None
    priority: Optional[str] = None
    is_read: bool = False
    thread_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Task(BaseModel):
    """Represents a task extracted from an email."""
    task_id: str
    title: str
    due_date: Optional[str] = None  # YYYY-MM-DD format
    source_email_id: str
    status: str = "todo"  # "todo", "in_progress", "done"
    notes: Optional[str] = None
    priority: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
        }


class Event(BaseModel):
    """Represents an event or deadline extracted from an email."""
    event_id: str
    type: str  # "meeting" or "deadline"
    title: str
    date: str  # YYYY-MM-DD format
    start_time: Optional[str] = None  # HH:MM format
    end_time: Optional[str] = None  # HH:MM format
    all_day: bool = False
    location: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    source_email_id: str
    confidence: float = 0.0
    status: str = "suggested"  # "suggested", "confirmed", "ignored"


class Reminder(BaseModel):
    """Represents a reminder linked to an email."""
    id: str
    email_id: str
    reminder_time: datetime
    note: str
    status: str = "pending"  # "pending", "done"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Draft(BaseModel):
    """Represents an email draft (reply or new email)."""
    id: str
    subject: str
    body: str
    recipient: Optional[str] = None
    reply_to_email_id: Optional[str] = None  # If this is a reply
    tone: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Category, action items, etc.
    suggested_followups: List[str] = Field(default_factory=list)
    status: str = "draft"  # "draft", "saved", "sent"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CategoryResult(BaseModel):
    """Result of email categorization."""
    category: str
    priority: str
    confidence: float = 0.0
    reasoning: Optional[str] = None

