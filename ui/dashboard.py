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
    st.header("Today's Dashboard")
    
    # Section: Statistics Overview
    with st.container():
        st.markdown("### Overview Statistics")
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            unread_count = len([e for e in st.session_state.emails if not e.is_read])
            stat_card("Unread Emails", str(unread_count), "")
        
        with col2:
            todo_count = len(get_tasks_by_status("todo"))
            stat_card("Tasks To Do", str(todo_count), "")
        
        with col3:
            upcoming_events = get_upcoming_events(1)
            stat_card("Today's Events", str(len(upcoming_events)), "")
        
        with col4:
            due_soon = get_tasks_due_soon(3)
            stat_card("Due Soon", str(len(due_soon)), "")
    
    st.divider()
    
    # Section: Main Content
    st.markdown("### Your Day at a Glance")
    
    # Add CSS for 2x2 grid with scrollable sections
    st.markdown(
        """
        <style>
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
            margin-top: 10px;
        }

        .dashboard-grid-item {
            border: 1px solid #ffffff;
            border-radius: 10px;
            padding: 8px 10px;
            box-shadow: 0 2px 2px rgba(0,0,0,0.1);
            background-color: #f8fafc;
            max-height: 260px;  /* fixed height, scrollable content */
            overflow-y: auto;
            margin-bottom: 10px;
        }

        .dashboard-grid-item h4 {
            margin-top: 0;
            margin-bottom: 8px;
            position: sticky;
            top: 0;
            background-color: #f8fafc;
            padding-bottom: 4px;
            z-index: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2x2 grid container
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)

    # === 1. High Priority Unread Emails ===
    st.markdown(
        '<div class="dashboard-grid-item"><h4>High Priority Unread Emails</h4>',
        unsafe_allow_html=True
    )
    high_priority = get_high_priority_emails()
    
    if high_priority:
        for email in high_priority[:5]:
            st.markdown(f"**{email.subject}**")
            st.caption(
                f"From: {email.sender_name} | {email.timestamp.strftime('%Y-%m-%d %H:%M')}"
            )
            if st.button("View", key=f"view_{email.id}"):
                st.session_state.selected_email_id = email.id
                st.session_state.page = "inbox"
                st.rerun()
            st.divider()
    else:
        st.info("No high priority unread emails.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # === 2. Upcoming Deadlines ===
    st.markdown(
        '<div class="dashboard-grid-item"><h4>Upcoming Deadlines</h4>',
        unsafe_allow_html=True
    )
    due_tasks = get_tasks_due_soon(7)
    
    if due_tasks:
        for task in sorted(due_tasks, key=lambda t: t.due_date or "")[:5]:
            task_card(task)
            st.divider()
    else:
        st.info("No upcoming deadlines.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # === 3. Next Meetings ===
    st.markdown(
        '<div class="dashboard-grid-item"><h4>Next Meetings</h4>',
        unsafe_allow_html=True
    )
    upcoming = get_upcoming_events(7)
    
    if upcoming:
        for event in upcoming[:5]:
            event_card(event)
            st.divider()
    else:
        st.info("No upcoming meetings.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # === 4. Top Tasks ===
    st.markdown(
        '<div class="dashboard-grid-item"><h4>Top Tasks</h4>',
        unsafe_allow_html=True
    )
    todo_tasks = get_tasks_by_status("todo")
    high_priority_tasks = [t for t in todo_tasks if t.priority == "High"]
    
    if high_priority_tasks:
        for task in high_priority_tasks[:5]:
            task_card(task)
            st.divider()
    elif todo_tasks:
        for task in todo_tasks[:5]:
            task_card(task)
            st.divider()
    else:
        st.info("No tasks to display.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Close grid container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick actions
    st.divider()
    st.markdown("### Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("View All Emails", key="quick_action_inbox"):
            st.session_state.page = "inbox"
            st.rerun()
    
    with col2:
        if st.button("View All Tasks", key="quick_action_tasks"):
            st.session_state.page = "tasks"
            st.rerun()
    
    with col3:
        if st.button("View Calendar", key="quick_action_calendar"):
            st.session_state.page = "calendar"
            st.rerun()
