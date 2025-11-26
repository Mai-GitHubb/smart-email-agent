"""
Dashboard view - Today's overview.
"""
import streamlit as st
from datetime import datetime, timedelta
from core.state import (
    get_upcoming_events, get_tasks_due_soon, get_high_priority_emails,
    get_tasks_by_status
)
from ui.components import info_card, stat_card, task_card, event_card


def render_dashboard():
    """Render the main dashboard view."""
    st.header("📊 Today's Dashboard")
    
    # Statistics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unread_count = len([e for e in st.session_state.emails if not e.is_read])
        stat_card("Unread Emails", str(unread_count), "📧")
    
    with col2:
        todo_count = len(get_tasks_by_status("todo"))
        stat_card("Tasks To Do", str(todo_count), "📋")
    
    with col3:
        upcoming_events = get_upcoming_events(1)
        stat_card("Today's Events", str(len(upcoming_events)), "📅")
    
    with col4:
        due_soon = get_tasks_due_soon(3)
        stat_card("Due Soon", str(len(due_soon)), "⏰")
    
    st.divider()
    
    # Main content columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 High Priority Unread Emails")
        high_priority = get_high_priority_emails()
        
        if high_priority:
            for email in high_priority[:5]:
                with st.container():
                    st.markdown(f"**{email.subject}**")
                    st.caption(f"From: {email.sender_name} | {email.timestamp.strftime('%Y-%m-%d %H:%M')}")
                    if st.button("View", key=f"view_{email.id}"):
                        st.session_state.selected_email_id = email.id
                    st.divider()
        else:
            st.info("No high priority unread emails.")
        
        st.subheader("⏰ Upcoming Deadlines")
        due_tasks = get_tasks_due_soon(7)
        
        if due_tasks:
            for task in sorted(due_tasks, key=lambda t: t.due_date or "")[:5]:
                with st.container():
                    task_card(task)
                    st.divider()
        else:
            st.info("No upcoming deadlines.")
    
    with col2:
        st.subheader("📅 Next Meetings")
        upcoming = get_upcoming_events(7)
        today = datetime.now().date()
        
        if upcoming:
            for event in upcoming[:5]:
                with st.container():
                    event_card(event)
                    st.divider()
        else:
            st.info("No upcoming meetings.")
        
        st.subheader("✅ Top Tasks")
        todo_tasks = get_tasks_by_status("todo")
        high_priority_tasks = [t for t in todo_tasks if t.priority == "High"]
        
        if high_priority_tasks:
            for task in high_priority_tasks[:5]:
                with st.container():
                    task_card(task)
                    st.divider()
        elif todo_tasks:
            for task in todo_tasks[:5]:
                with st.container():
                    task_card(task)
                    st.divider()
        else:
            st.info("No tasks to display.")
    
    # Quick actions
    st.divider()
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 View All Emails", key="quick_action_inbox"):
            st.session_state.page = "inbox"
            st.rerun()
    
    with col2:
        if st.button("📋 View All Tasks", key="quick_action_tasks"):
            st.session_state.page = "tasks"
            st.rerun()
    
    with col3:
        if st.button("📅 View Calendar", key="quick_action_calendar"):
            st.session_state.page = "calendar"
            st.rerun()

