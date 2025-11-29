"""
Main layout components for the app.
"""
import streamlit as st


def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.title("Smart Email Agent")
        st.divider()
        
        # Navigation
        pages = {
            "Dashboard": "dashboard",
            "Inbox": "inbox",
            "Email Agent": "email_agent",
            "Calendar": "calendar",
            "Tasks": "tasks",
            "Files": "files",
            "Drafts": "drafts",
            "Settings": "settings"
        }
        
        # Get current page index
        current_page = st.session_state.get('page', 'dashboard')
        page_names = list(pages.keys())
        page_values = list(pages.values())
        
        # Find index of current page
        try:
            current_index = page_values.index(current_page)
        except ValueError:
            current_index = 0
        
        selected = st.radio(
            "Navigation",
            page_names,
            index=current_index,
            label_visibility="collapsed"
        )
        
        st.session_state.page = pages[selected]
        
        st.divider()
        
        # Quick stats
        st.markdown("### Quick Stats")
        unread = len([e for e in st.session_state.emails if not e.is_read])
        st.metric("Unread", unread)
        
        todo_tasks = len([t for t in st.session_state.tasks if t.status == "todo"])
        st.metric("Tasks", todo_tasks)
        
        upcoming_events = len([e for e in st.session_state.events 
                              if e.status == "confirmed"])
        st.metric("Events", upcoming_events)
        
        st.divider()
        
        # Mode indicator
        mode_text = "Mock" if st.session_state.mode == "mock" else "Gmail API"
        st.caption(f"Mode: {mode_text}")

