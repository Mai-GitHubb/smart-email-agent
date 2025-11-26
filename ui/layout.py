"""
Main layout components for the app.
"""
import streamlit as st


def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.title("📧 Smart Email Agent")
        st.divider()
        
        # Navigation
        pages = {
            "Dashboard": "dashboard",
            "Inbox": "inbox",
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
        
        # Chat with inbox
        st.subheader("💬 Ask Your Inbox")
        query = st.text_input("Ask a question about your inbox", key="inbox_query_input")
        
        if st.button("Ask", key="ask_button"):
            if query and st.session_state.emails:
                try:
                    from core.llm_client import LLMClient
                    
                    # Build context
                    context = {
                        "total_emails": len(st.session_state.emails),
                        "unread_count": len([e for e in st.session_state.emails if not e.is_read]),
                        "categories": ", ".join(set([e.category for e in st.session_state.emails if e.category])),
                        "tasks_summary": f"{len(st.session_state.tasks)} tasks",
                        "events_summary": f"{len(st.session_state.events)} events"
                    }
                    
                    llm_client = LLMClient()
                    prompt = st.session_state.prompts.get('inbox_query', 
                                                               "Answer the user's question about their inbox.")
                    
                    with st.spinner("Thinking..."):
                        response = llm_client.process_inbox_query(query, context, prompt)
                    
                    st.info(response)
                except Exception as e:
                    st.error(f"Error processing query: {e}")
        
        st.divider()
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        unread = len([e for e in st.session_state.emails if not e.is_read])
        st.metric("Unread", unread)
        
        todo_tasks = len([t for t in st.session_state.tasks if t.status == "todo"])
        st.metric("Tasks", todo_tasks)
        
        upcoming_events = len([e for e in st.session_state.events 
                              if e.status == "confirmed"])
        st.metric("Events", upcoming_events)
        
        st.divider()
        
        # Mode indicator
        mode_icon = "📧" if st.session_state.mode == "mock" else "🔐"
        st.caption(f"{mode_icon} Mode: {st.session_state.mode.upper()}")

