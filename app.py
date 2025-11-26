"""
Smart Email Agent - Main Streamlit Application

Entry point for the Smart Email Agent application.
"""
import streamlit as st
from core.state import initialize_state
from ui.layout import render_sidebar
from ui.dashboard import render_dashboard
from ui.inbox_view import render_inbox
from ui.calendar_view import render_calendar
from ui.tasks_view import render_tasks
from ui.files_view import render_files
from ui.drafts_view import render_drafts
from ui.settings_view import render_settings
import config


def main():
    """Main application entry point."""
    # Page config
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize state
    initialize_state()
    
    # Set default page if not set
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    page = st.session_state.page
    
    if page == "dashboard":
        render_dashboard()
    elif page == "inbox":
        render_inbox()
    elif page == "calendar":
        render_calendar()
    elif page == "tasks":
        render_tasks()
    elif page == "files":
        render_files()
    elif page == "drafts":
        render_drafts()
    elif page == "settings":
        render_settings()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()

