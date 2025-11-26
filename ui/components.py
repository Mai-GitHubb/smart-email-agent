"""
Reusable UI components for the Smart Email Agent.
"""
import streamlit as st
from typing import Optional
from core.models import Email, Task, Event


def priority_badge(priority: Optional[str]) -> str:
    """Get emoji/icon for priority level."""
    if priority == "High":
        return "🔴"
    elif priority == "Medium":
        return "🟡"
    elif priority == "Low":
        return "🟢"
    return "⚪"


def category_icon(category: Optional[str]) -> str:
    """Get emoji/icon for category."""
    icons = {
        "Work": "💼",
        "Personal": "👤",
        "To-Do": "✅",
        "Newsletter": "📰",
        "Spam": "🚫",
        "Meeting": "📅",
        "Deadline": "⏰",
        "Other": "📧"
    }
    return icons.get(category, "📧")


def email_card(email: Email, show_body: bool = False):
    """Display an email as a card."""
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown(f"### {category_icon(email.category)}")
        st.markdown(f"{priority_badge(email.priority)}")
        if not email.is_read:
            st.markdown("**NEW**")
    
    with col2:
        st.markdown(f"**{email.subject}**")
        st.caption(f"From: {email.sender_name} ({email.sender})")
        st.caption(f"📅 {email.timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        if email.category:
            st.caption(f"Category: {email.category} | Priority: {email.priority}")
        
        if show_body:
            with st.expander("View Email Body"):
                st.text(email.body)
        
        if email.has_attachments:
            st.caption(f"📎 {len(email.attachments)} attachment(s)")


def task_card(task: Task):
    """Display a task as a card."""
    status_icons = {
        "todo": "📋",
        "in_progress": "🔄",
        "done": "✅"
    }
    
    icon = status_icons.get(task.status, "📋")
    st.markdown(f"### {icon} {task.title}")
    
    if task.due_date:
        st.caption(f"Due: {task.due_date}")
    
    if task.notes:
        with st.expander("Notes"):
            st.text(task.notes)
    
    if task.priority:
        st.caption(f"Priority: {priority_badge(task.priority)}")


def event_card(event: Event, show_actions: bool = False):
    """Display an event as a card."""
    type_icons = {
        "meeting": "🤝",
        "deadline": "⏰"
    }
    
    icon = type_icons.get(event.type, "📅")
    st.markdown(f"### {icon} {event.title}")
    st.caption(f"Date: {event.date}")
    
    if event.start_time:
        st.caption(f"Time: {event.start_time}" + (f" - {event.end_time}" if event.end_time else ""))
    
    if event.location:
        st.caption(f"📍 {event.location}")
    
    if event.participants:
        st.caption(f"👥 {', '.join(event.participants[:3])}")
    
    if show_actions and event.status == "suggested":
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✓ Confirm", key=f"confirm_{event.event_id}"):
                return "confirm"
        with col2:
            if st.button("✏️ Edit", key=f"edit_{event.event_id}"):
                return "edit"
        with col3:
            if st.button("✕ Ignore", key=f"ignore_{event.event_id}"):
                return "ignore"
    
    return None


def info_card(title: str, content: str, icon: str = "ℹ️"):
    """Display an info card."""
    st.markdown(f"### {icon} {title}")
    st.markdown(content)


def stat_card(label: str, value: str, icon: str = ""):
    """Display a statistics card."""
    st.metric(label=f"{icon} {label}", value=value)

