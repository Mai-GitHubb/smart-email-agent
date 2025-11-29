"""
Session state management helpers.

Provides utilities for managing Streamlit session state.
"""
import streamlit as st
from typing import List, Dict, Any, Optional
from core.models import Email, Task, Event, Reminder
from datetime import datetime


def initialize_state():
    """
    Initialize all session state variables.
    
    This function sets up all the necessary session state variables for the application.
    It ensures that:
    - All data structures (emails, tasks, events, etc.) are initialized
    - Prompts are loaded from persistent storage (data/prompts.json) or defaults
    - Mode is set to "mock" by default (can be changed to "gmail" in settings)
    
    Session state persists across reruns in Streamlit, allowing data to be maintained
    throughout the user's session.
    """
    # Email storage - list of Email objects loaded from mock inbox or Gmail API
    if 'emails' not in st.session_state:
        st.session_state.emails = []
    
    # Task storage - list of Task objects extracted from emails
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    
    # Event storage - list of Event objects extracted from emails (meetings/deadlines)
    if 'events' not in st.session_state:
        st.session_state.events = []
    
    # Reminder storage - list of Reminder objects linked to emails
    if 'reminders' not in st.session_state:
        st.session_state.reminders = []
    
    # Currently selected email ID (for detail view)
    if 'selected_email_id' not in st.session_state:
        st.session_state.selected_email_id = None
    
    # Application mode: "mock" for mock inbox, "gmail" for Gmail API
    if 'mode' not in st.session_state:
        st.session_state.mode = "mock"  # "mock" or "gmail"
    
    # Load prompts from persistent storage (data/prompts.json)
    # If file doesn't exist, uses default prompts from core.prompts
    # This is the "Prompt Brain" - user-defined prompts that control LLM behavior
    if 'prompts' not in st.session_state:
        from core.prompt_storage import load_prompts
        st.session_state.prompts = load_prompts()
    
    # Draft storage - list of Draft objects (new emails and replies)
    # Each draft includes metadata, suggested follow-ups, etc.
    if 'drafts' not in st.session_state:
        st.session_state.drafts = []
    
    # Processing cache - stores processing results to avoid redundant LLM calls
    if 'processing_cache' not in st.session_state:
        st.session_state.processing_cache = {}


def get_email(email_id: str) -> Optional[Email]:
    """Get an email by ID."""
    for email in st.session_state.emails:
        if email.id == email_id:
            return email
    return None


def add_task(task: Task):
    """Add a task to the state."""
    # Check if task already exists
    if not any(t.task_id == task.task_id for t in st.session_state.tasks):
        st.session_state.tasks.append(task)


def add_event(event: Event):
    """Add an event to the state."""
    # Check if event already exists
    if not any(e.event_id == event.event_id for e in st.session_state.events):
        st.session_state.events.append(event)


def add_reminder(reminder: Reminder):
    """Add a reminder to the state."""
    if not any(r.id == reminder.id for r in st.session_state.reminders):
        st.session_state.reminders.append(reminder)


def get_tasks_by_status(status: str) -> List[Task]:
    """Get tasks filtered by status."""
    return [t for t in st.session_state.tasks if t.status == status]


def get_events_by_date(date: str) -> List[Event]:
    """Get events for a specific date (YYYY-MM-DD)."""
    return [e for e in st.session_state.events if e.date == date and e.status == "confirmed"]


def get_upcoming_events(days: int = 7) -> List[Event]:
    """Get upcoming events within the next N days."""
    from datetime import datetime, timedelta
    today = datetime.now().date()
    end_date = (today + timedelta(days=days)).isoformat()
    
    upcoming = []
    for event in st.session_state.events:
        if event.status == "confirmed" and today.isoformat() <= event.date <= end_date:
            upcoming.append(event)
    
    return sorted(upcoming, key=lambda e: e.date)


def get_tasks_due_soon(days: int = 7) -> List[Task]:
    """Get tasks due within the next N days."""
    from datetime import datetime, timedelta
    today = datetime.now().date()
    end_date = (today + timedelta(days=days)).isoformat()
    
    due_soon = []
    for task in st.session_state.tasks:
        if task.due_date and task.status != "done":
            if today.isoformat() <= task.due_date <= end_date:
                due_soon.append(task)
    
    return sorted(due_soon, key=lambda t: t.due_date or "")


def get_tasks_by_date(date: str) -> List[Task]:
    """Get tasks that are due on a specific date (YYYY-MM-DD)."""
    return [
        t
        for t in st.session_state.tasks
        if t.due_date == date and t.status != "done"
    ]


def get_high_priority_emails() -> List[Email]:
    """Get high priority unread emails."""
    return [
        e for e in st.session_state.emails
        if e.priority == "High" and not e.is_read
    ]


def get_emails_by_category(category: str) -> List[Email]:
    """Get emails filtered by category."""
    return [e for e in st.session_state.emails if e.category == category]


def get_emails_by_sender(sender_email: str) -> List[Email]:
    """Get emails from a specific sender."""
    return [e for e in st.session_state.emails if e.sender == sender_email]


def update_task_status(task_id: str, new_status: str):
    """Update a task's status."""
    for task in st.session_state.tasks:
        if task.task_id == task_id:
            task.status = new_status
            break


def confirm_event(event_id: str):
    """Confirm an event (move from suggested to confirmed)."""
    for event in st.session_state.events:
        if event.event_id == event_id:
            event.status = "confirmed"
            break


def ignore_event(event_id: str):
    """Ignore an event."""
    for event in st.session_state.events:
        if event.event_id == event_id:
            event.status = "ignored"
            break

