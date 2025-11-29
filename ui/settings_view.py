"""
Settings view - Mode selection and Prompt Brain.
"""
import streamlit as st
from core import prompts


def render_settings():
    """Render the settings view."""
    st.header("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["Mode Selection", "Prompt Brain"])
    
    with tab1:
        render_mode_selection()
    
    with tab2:
        render_prompt_brain()


def render_mode_selection():
    """Render mode selection interface."""
    st.subheader("📡 Email Source Mode")
    
    current_mode = st.session_state.mode
    
    mode = st.radio(
        "Select Email Source",
        ["Mock Inbox", "Gmail API"],
        index=0 if current_mode == "mock" else 1
    )
    
    if mode == "Mock Inbox":
        st.info("📧 Using mock inbox data from local JSON file.")
        st.markdown("""
        **Mock Inbox Mode:**
        - Loads sample emails from `data/mock_inbox.json`
        - No authentication required
        - Perfect for testing and demos
        """)
        
        if st.button("Load Mock Inbox"):
            from core.mock_data_loader import load_mock_inbox
            from core.processors import EmailProcessor
            from core.llm_client import LLMClient
            
            with st.spinner("Loading mock inbox..."):
                emails = load_mock_inbox()
                st.session_state.emails = emails
                st.session_state.mode = "mock"
                st.success(f"Loaded {len(emails)} emails from mock inbox!")
                
                # Auto-process emails
                if st.session_state.emails:
                    try:
                        llm_client = LLMClient()
                        processor = EmailProcessor(llm_client)
                        
                        with st.spinner("Processing emails..."):
                            for email in st.session_state.emails[:10]:  # Process first 10
                                result = processor.process_email(email)
                                
                                # Add tasks and events to state
                                for task in result['tasks']:
                                    from core.state import add_task
                                    add_task(task)
                                
                                for event in result['events']:
                                    from core.state import add_event
                                    add_event(event)
                        
                        st.success("Emails processed!")
                    except Exception as e:
                        st.warning(f"Could not process emails: {e}")
    
    else:  # Gmail API
        st.info("🔐 Gmail API mode requires OAuth authentication.")
        st.markdown("""
        **Gmail API Mode:**
        - Connect to your real Gmail account
        - Requires OAuth 2.0 credentials
        - Read-only access (no auto-sending)
        
        **Setup Instructions:**
        1. Create a Google Cloud Project
        2. Enable Gmail API
        3. Create OAuth 2.0 credentials
        4. Save credentials as `credentials.json`
        5. Click "Connect to Gmail" below
        """)
        
        if st.button("Connect to Gmail"):
            from core.gmail_client import GmailClient
            
            with st.spinner("Authenticating with Gmail..."):
                gmail_client = GmailClient()
                if gmail_client.authenticate():
                    st.session_state.gmail_client = gmail_client
                    st.session_state.mode = "gmail"
                    st.success("Connected to Gmail!")
                    
                    # Fetch emails
                    with st.spinner("Fetching emails..."):
                        # Fetch up to 50 emails
                        emails = gmail_client.fetch_emails(max_results=50)
                        st.session_state.emails = emails
                        st.success(f"Fetched {len(emails)} emails!")
                        
                        # Auto-process
                        if st.session_state.emails:
                            try:
                                from core.processors import EmailProcessor
                                from core.llm_client import LLMClient
                                
                                llm_client = LLMClient()
                                processor = EmailProcessor(llm_client)
                                
                                with st.spinner("Processing emails..."):
                                    for email in st.session_state.emails[:10]:
                                        result = processor.process_email(email)
                                        
                                        for task in result['tasks']:
                                            from core.state import add_task
                                            add_task(task)
                                        
                                        for event in result['events']:
                                            from core.state import add_event
                                            add_event(event)
                                
                                st.success("Emails processed!")
                            except Exception as e:
                                st.warning(f"Could not process emails: {e}")
                else:
                    st.error("Failed to authenticate with Gmail. Please check your credentials.")


def render_prompt_brain():
    """Render prompt configuration interface."""
    st.subheader("🧠 Prompt Brain - Customize LLM Prompts")
    
    st.markdown("""
    Edit the prompts used by the LLM for different tasks. Changes are saved to session state.
    """)
    
    # Prompt editor tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Categorization",
        "Task Extraction",
        "Event Extraction",
        "Reply Generation",
        "Other Prompts"
    ])
    
    with tab1:
        st.markdown("### Email Categorization Prompt")
        categorization_prompt = st.text_area(
            "Prompt",
            value=st.session_state.prompts['categorization'],
            height=200,
            key="edit_categorization"
        )
        if st.button("Save Categorization Prompt"):
            st.session_state.prompts['categorization'] = categorization_prompt
            from core.prompt_storage import save_prompts
            save_prompts(st.session_state.prompts)
            st.success("Saved to file!")
    
    with tab2:
        st.markdown("### Task Extraction Prompt")
        task_prompt = st.text_area(
            "Prompt",
            value=st.session_state.prompts['task_extraction'],
            height=200,
            key="edit_task_extraction"
        )
        if st.button("Save Task Extraction Prompt"):
            st.session_state.prompts['task_extraction'] = task_prompt
            from core.prompt_storage import save_prompts
            save_prompts(st.session_state.prompts)
            st.success("Saved to file!")
    
    with tab3:
        st.markdown("### Event Extraction Prompt")
        event_prompt = st.text_area(
            "Prompt",
            value=st.session_state.prompts['event_extraction'],
            height=200,
            key="edit_event_extraction"
        )
        if st.button("Save Event Extraction Prompt"):
            st.session_state.prompts['event_extraction'] = event_prompt
            from core.prompt_storage import save_prompts
            save_prompts(st.session_state.prompts)
            st.success("Saved to file!")
    
    with tab4:
        st.markdown("### Reply Generation Prompt")
        reply_prompt = st.text_area(
            "Prompt",
            value=st.session_state.prompts['reply_generation'],
            height=200,
            key="edit_reply_generation"
        )
        if st.button("Save Reply Generation Prompt"):
            st.session_state.prompts['reply_generation'] = reply_prompt
            from core.prompt_storage import save_prompts
            save_prompts(st.session_state.prompts)
            st.success("Saved to file!")
    
    with tab5:
        st.markdown("### Other Prompts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Explanation Prompt")
            explanation_prompt = st.text_area(
                "Prompt",
                value=st.session_state.prompts['explanation'],
                height=150,
                key="edit_explanation"
            )
            if st.button("Save Explanation Prompt"):
                st.session_state.prompts['explanation'] = explanation_prompt
                from core.prompt_storage import save_prompts
                save_prompts(st.session_state.prompts)
                st.success("Saved to file!")
        
        with col2:
            st.markdown("#### Tone Check Prompt")
            tone_check_prompt = st.text_area(
                "Prompt",
                value=st.session_state.prompts['tone_check'],
                height=150,
                key="edit_tone_check"
            )
            if st.button("Save Tone Check Prompt"):
                st.session_state.prompts['tone_check'] = tone_check_prompt
                from core.prompt_storage import save_prompts
                save_prompts(st.session_state.prompts)
                st.success("Saved to file!")
        
        st.markdown("#### Sender Context Prompt")
        sender_context_prompt = st.text_area(
            "Prompt",
            value=st.session_state.prompts['sender_context'],
            height=150,
            key="edit_sender_context"
        )
        if st.button("Save Sender Context Prompt"):
            st.session_state.prompts['sender_context'] = sender_context_prompt
            from core.prompt_storage import save_prompts
            save_prompts(st.session_state.prompts)
            st.success("Saved to file!")
        
        st.markdown("#### New Draft Generation Prompt")
        new_draft_prompt = st.text_area(
            "Prompt",
            value=st.session_state.prompts.get('new_draft_generation', ''),
            height=150,
            key="edit_new_draft_generation"
        )
        if st.button("Save New Draft Generation Prompt"):
            st.session_state.prompts['new_draft_generation'] = new_draft_prompt
            from core.prompt_storage import save_prompts
            save_prompts(st.session_state.prompts)
            st.success("Saved to file!")
    
    # Reset to defaults
    st.divider()
    if st.button("🔄 Reset All Prompts to Defaults"):
        from core.prompt_storage import get_default_prompts, save_prompts
        st.session_state.prompts = get_default_prompts()
        save_prompts(st.session_state.prompts)
        st.success("All prompts reset to defaults and saved!")

