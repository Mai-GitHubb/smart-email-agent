"""
Calendar view - Events and deadlines.
"""
import calendar
from datetime import datetime, timedelta, date

import streamlit as st

from core.state import get_events_by_date, confirm_event, ignore_event, get_tasks_by_date
from ui.components import event_card
from core.models import Event
from core.google_calendar_client import GoogleCalendarClient
from core.date_utils import parse_date, normalize_date


def render_calendar():
    """Render the calendar view."""
    st.header("Calendar & Events")

    # Top-level actions
    with st.expander("🔁 Sync Tasks to Google Calendar", expanded=False):
        st.markdown(
            "Sync all tasks with a due date to your Google Calendar as all-day events."
        )
        if st.button("Sync Tasks", key="sync_tasks_to_calendar"):
            _sync_tasks_to_google_calendar()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Calendar", "Suggested Events"])

    with tab1:
        render_calendar_view()

    with tab2:
        render_suggested_events()


def render_calendar_view():
    """Render the calendar month view with tasks and events."""
    # Section: Month Selector
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_date: date = st.date_input("Select Month", datetime.now().date())
        with col2:
            st.write("")  # Spacing
        year = selected_date.year
        month = selected_date.month

        st.markdown(f"## {calendar.month_name[month]} {year}")
        st.markdown("---")

    # Build calendar grid
    month_calendar = calendar.monthcalendar(year, month)
    weekday_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_cols = st.columns(7)
    for idx, day_name in enumerate(weekday_headers):
        header_cols[idx].markdown(f"**{day_name}**")

    for week in month_calendar:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write(" ")
                    continue

                # Date string
                current_date = date(year, month, day)
                current_date_str = current_date.isoformat()

                # Header with day number
                st.markdown(f"<div style='font-weight:600; font-size:1.1rem; margin-bottom:5px;'>{day}</div>", unsafe_allow_html=True)

                # Events and tasks for this day
                events = get_events_by_date(current_date_str)
                tasks = get_tasks_by_date(current_date_str)

                # Show tasks first (like a todo calendar) - prioritize tasks
                if tasks:
                    for t in tasks[:3]:  # Show up to 3 tasks
                        status_color = "#16a34a" if t.status == "todo" else "#f59e0b" if t.status == "in_progress" else "#6b7280"
                        st.markdown(
                            f"<div style='font-size:0.7rem;color:{status_color};margin:2px 0;padding:2px;background:#f0f9ff;border-radius:4px;'>📝 {t.title[:25]}{'...' if len(t.title) > 25 else ''}</div>",
                            unsafe_allow_html=True,
                        )

                # Then show events
                if events:
                    for ev in events[:2]:  # limit to avoid clutter
                        icon = "🤝" if ev.type == "meeting" else "⏰"
                        st.markdown(
                            f"<div style='font-size:0.7rem;color:#0369a1;margin:2px 0;padding:2px;background:#eff6ff;border-radius:4px;'>{icon} {ev.title[:25]}{'...' if len(ev.title) > 25 else ''}</div>",
                            unsafe_allow_html=True,
                        )
                
                # Show count if more items
                total_items = len(tasks) + len(events)
                if total_items > 5:
                    st.caption(f"+{total_items - 5} more")

    # Section: Detailed Task & Event List
    st.divider()
    st.subheader("All Tasks & Events")
    st.caption("Click on any date below to see detailed tasks and events")
    
    # Get all upcoming tasks and events
    from core.state import get_tasks_due_soon, get_upcoming_events
    
    all_tasks = [t for t in st.session_state.tasks if t.due_date and t.status != "done"]
    all_events = [e for e in st.session_state.events if e.status == "confirmed"]
    
    if not all_tasks and not all_events:
        st.info("No upcoming tasks or events. Process emails to extract tasks and events.")
        return
    
    # Group by date
    from collections import defaultdict
    items_by_date = defaultdict(lambda: {"tasks": [], "events": []})
    
    for task in all_tasks:
        if task.due_date:
            items_by_date[task.due_date]["tasks"].append(task)
    
    for event in all_events:
        items_by_date[event.date]["events"].append(event)
    
    # Display sorted by date
    for date_str in sorted(items_by_date.keys()):
        items = items_by_date[date_str]
        # Parse date safely
        date_obj = parse_date(date_str)
        if not date_obj:
            # Skip invalid dates
            continue
        
        with st.expander(f"{date_obj.strftime('%B %d, %Y')} ({len(items['tasks'])} tasks, {len(items['events'])} events)", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Tasks:**")
                if items['tasks']:
                    for task in items['tasks']:
                        status_icon = "✅" if task.status == "done" else "📋" if task.status == "todo" else "🔄"
                        st.markdown(f"{status_icon} **{task.title}**")
                        if task.notes:
                            st.caption(f"   {task.notes}")
                else:
                    st.caption("No tasks")
            
            with col2:
                st.markdown("**Events:**")
                if items['events']:
                    for event in items['events']:
                        icon = "🤝" if event.type == "meeting" else "⏰"
                        st.markdown(f"{icon} **{event.title}**")
                        if event.start_time:
                            st.caption(f"   {event.start_time}" + (f" - {event.end_time}" if event.end_time else ""))
                        if event.location:
                            st.caption(f"   📍 {event.location}")
                else:
                    st.caption("No events")


def _sync_tasks_to_google_calendar():
    """Sync all tasks with due dates to Google Calendar."""
    from core.state import get_tasks_due_soon

    tasks = [t for t in st.session_state.tasks if t.due_date]
    if not tasks:
        st.info("No tasks with due dates to sync.")
        return

    client = GoogleCalendarClient()
    if not client.authenticate():
        st.error(
            "Could not authenticate with Google Calendar. "
            "Make sure credentials are configured and Calendar API is enabled."
        )
        return

    synced = 0
    for task in tasks:
        event_id = client.add_task_as_event(task)
        if event_id:
            synced += 1

    st.success(f"Synced {synced} task(s) to Google Calendar.")


def render_suggested_events():
    """Render suggested events from email extraction."""
    st.subheader("Suggested Events from Emails")
    st.caption("Review and confirm events extracted from your emails")
    
    suggested = [e for e in st.session_state.events if e.status == "suggested"]
    
    if not suggested:
        st.info("No suggested events. Process emails to extract events.")
        return
    
    # Summary section
    with st.container():
        st.markdown(f"**Found {len(suggested)} suggested event(s)**")
        st.markdown("---")
    
    for event in suggested:
        with st.container():
            st.markdown("---")
            
            # Event details
            type_icon = "🤝" if event.type == "meeting" else "⏰"
            st.markdown(f"### {type_icon} {event.title}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Date:** {event.date}")
                if event.start_time:
                    st.markdown(f"**Time:** {event.start_time}" + (f" - {event.end_time}" if event.end_time else ""))
                if event.location:
                    st.markdown(f"**Location:** {event.location}")
            
            with col2:
                if event.participants:
                    st.markdown(f"**Participants:** {', '.join(event.participants)}")
                st.markdown(f"**Confidence:** {event.confidence:.0%}")
                st.caption(f"Source: Email {event.source_email_id}")
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✓ Confirm & Add", key=f"confirm_{event.event_id}"):
                    confirm_event(event.event_id)
                    # Sync to Google Calendar
                    try:
                        from core.google_calendar_client import GoogleCalendarClient
                        calendar_client = GoogleCalendarClient()
                        if calendar_client.authenticate():
                            event_id = calendar_client.add_event(event)
                            if event_id:
                                st.success(f"Event confirmed and synced to Google Calendar! (Event ID: {event_id})")
                            else:
                                st.success("Event confirmed! (Calendar sync failed - check credentials)")
                        else:
                            st.success("Event confirmed! (Calendar sync skipped - authentication failed)")
                    except Exception as e:
                        st.success(f"Event confirmed! (Calendar sync error: {str(e)})")
                    st.rerun()
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{event.event_id}"):
                    st.session_state.editing_event_id = event.event_id
                    st.rerun()
            
            with col3:
                if st.button("✕ Ignore", key=f"ignore_{event.event_id}"):
                    ignore_event(event.event_id)
                    st.info("Event ignored.")
                    st.rerun()
            
            st.divider()
    
    # Edit event dialog
    if 'editing_event_id' in st.session_state:
        event_to_edit = next((e for e in suggested if e.event_id == st.session_state.editing_event_id), None)
        if event_to_edit:
            with st.expander("Edit Event", expanded=True):
                new_title = st.text_input("Title", value=event_to_edit.title)
                # Parse date safely
                parsed_date = parse_date(event_to_edit.date)
                if parsed_date:
                    new_date = st.date_input("Date", value=parsed_date)
                else:
                    st.error(f"Invalid date format: {event_to_edit.date}")
                    new_date = st.date_input("Date", value=datetime.now().date())
                
                # Parse start time safely
                new_start_time = None
                if event_to_edit.start_time:
                    try:
                        new_start_time = st.time_input("Start Time", value=datetime.strptime(event_to_edit.start_time, "%H:%M").time())
                    except:
                        new_start_time = st.time_input("Start Time", value=None)
                else:
                    new_start_time = st.time_input("Start Time", value=None)
                
                new_location = st.text_input("Location", value=event_to_edit.location or "")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Changes"):
                        # Update event
                        event_to_edit.title = new_title
                        event_to_edit.date = new_date.isoformat()
                        if new_start_time:
                            event_to_edit.start_time = new_start_time.strftime("%H:%M")
                        event_to_edit.location = new_location
                        event_to_edit.status = "confirmed"
                        del st.session_state.editing_event_id
                        st.success("Event updated!")
                        st.rerun()
                
                with col2:
                    if st.button("Cancel"):
                        del st.session_state.editing_event_id
                        st.rerun()

