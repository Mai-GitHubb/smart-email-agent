"""
Calendar view - Events and deadlines.
"""
import streamlit as st
from datetime import datetime, timedelta
from core.state import get_events_by_date, confirm_event, ignore_event
from ui.components import event_card
from core.models import Event


def render_calendar():
    """Render the calendar view."""
    st.header("📅 Calendar & Events")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Calendar", "Suggested Events"])
    
    with tab1:
        render_calendar_view()
    
    with tab2:
        render_suggested_events()


def render_calendar_view():
    """Render the calendar month view."""
    st.subheader("Month View")
    
    # Date selector
    selected_date = st.date_input("Select Date", datetime.now().date())
    selected_date_str = selected_date.isoformat()
    
    # Get events for selected date
    events = get_events_by_date(selected_date_str)
    
    st.markdown(f"### Events on {selected_date.strftime('%B %d, %Y')}")
    
    if events:
        for event in events:
            with st.container():
                event_card(event, show_actions=False)
                st.divider()
    else:
        st.info("No events scheduled for this date.")
    
    # Upcoming events list
    st.subheader("Upcoming Events (Next 7 Days)")
    from core.state import get_upcoming_events
    
    upcoming = get_upcoming_events(7)
    if upcoming:
        for event in upcoming:
            with st.container():
                event_card(event, show_actions=False)
                st.divider()
    else:
        st.info("No upcoming events.")


def render_suggested_events():
    """Render suggested events from email extraction."""
    st.subheader("📋 Suggested Events from Emails")
    
    suggested = [e for e in st.session_state.events if e.status == "suggested"]
    
    if not suggested:
        st.info("No suggested events. Process emails to extract events.")
        return
    
    st.markdown(f"Found {len(suggested)} suggested event(s)")
    
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
                    st.success("Event confirmed!")
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
                new_date = st.date_input("Date", value=datetime.fromisoformat(event_to_edit.date).date())
                new_start_time = st.time_input("Start Time", value=datetime.strptime(event_to_edit.start_time, "%H:%M").time() if event_to_edit.start_time else None)
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

