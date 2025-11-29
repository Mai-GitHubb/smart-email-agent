"""
Smart Email Agent - Main Streamlit Application

Entry point for the Smart Email Agent application.
"""
import streamlit as st
from core.state import initialize_state
from ui.layout import render_sidebar
from ui.dashboard import render_dashboard
from ui.inbox_view import render_inbox
from ui.email_agent_view import render_email_agent
from ui.calendar_view import render_calendar
from ui.tasks_view import render_tasks
from ui.files_view import render_files
from ui.drafts_view import render_drafts
from ui.settings_view import render_settings
import config


def main():
    """
    Main application entry point.
    
    This function:
    1. Configures Streamlit page settings
    2. Initializes session state (emails, tasks, events, prompts, etc.)
    3. Renders the sidebar navigation
    4. Routes to the appropriate view based on the current page
    
    The application supports 8 main views:
    - dashboard: Overview of emails, tasks, and events
    - inbox: Email list and detail view
    - email_agent: Chat interface for email interaction
    - calendar: Calendar view with tasks and events
    - tasks: Kanban task board
    - files: Attachments hub
    - drafts: Draft management (new emails and replies)
    - settings: Configuration and Prompt Brain
    """
    # Configure Streamlit page settings
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout="wide",  # Use wide layout for better space utilization
        initial_sidebar_state="expanded",  # Sidebar open by default
    )

    # Initialize all session state variables
    # This loads prompts from file, sets up empty lists for emails/tasks/events, etc.
    initialize_state()
    
    # Set default page to dashboard if not already set
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Render sidebar with navigation menu and quick stats
    render_sidebar()
    
    # Route to the appropriate view based on the current page
    # Each view is a separate module in the ui/ directory
    page = st.session_state.page
    
    if page == "dashboard":
        render_dashboard()
    elif page == "inbox":
        render_inbox()
    elif page == "email_agent":
        render_email_agent()  # Dedicated Email Agent chat interface
    elif page == "calendar":
        render_calendar()
    elif page == "tasks":
        render_tasks()
    elif page == "files":
        render_files()
    elif page == "drafts":
        render_drafts()  # Draft management (new emails and replies)
    elif page == "settings":
        render_settings()  # Includes Prompt Brain for customizing LLM prompts
    else:
        # Fallback to dashboard for unknown pages
        render_dashboard()


if __name__ == "__main__":
    main()

