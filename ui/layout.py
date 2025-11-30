import streamlit as st


def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.title("Smart Email Agent")
        st.divider()

        # 🔹 Inbox source controls (new)
        st.markdown("### Inbox Source")

        mode = st.session_state.get("mode", "mock")
        mode_text = "Mock Inbox" if mode == "mock" else "Gmail API"
        st.caption(f"Current mode: {mode_text}")

        col1, col2 = st.columns(2)

        # ---- Load Mock Inbox button ----
        with col1:
            if st.button("Load Mock", key="sidebar_load_mock"):
                from core.mock_data_loader import load_mock_inbox
                from core.processors import EmailProcessor
                from core.llm_client import LLMClient
                from core.state import add_task, add_event

                with st.spinner("Loading mock inbox..."):
                    emails = load_mock_inbox()
                    st.session_state.emails = emails
                    st.session_state.mode = "mock"

                if st.session_state.emails:
                    try:
                        llm_client = LLMClient()
                        processor = EmailProcessor(llm_client)

                        with st.spinner("Processing emails..."):
                            for email in st.session_state.emails[:10]:  # Process first 10
                                result = processor.process_email(email)
                                for task in result["tasks"]:
                                    add_task(task)
                                for event in result["events"]:
                                    add_event(event)

                        st.success(f"Loaded and processed {len(emails)} mock emails!")
                    except Exception as e:
                        st.warning(f"Could not process emails: {e}")

        # ---- Connect Gmail button ----
        with col2:
            if st.button("Connect Gmail", key="sidebar_connect_gmail"):
                from core.gmail_client import GmailClient
                from core.processors import EmailProcessor
                from core.llm_client import LLMClient
                from core.state import add_task, add_event

                with st.spinner("Authenticating with Gmail..."):
                    gmail_client = GmailClient()
                    if gmail_client.authenticate():
                        st.session_state.gmail_client = gmail_client
                        st.session_state.mode = "gmail"

                        with st.spinner("Fetching emails..."):
                            emails = gmail_client.fetch_emails(max_results=50)
                            st.session_state.emails = emails

                        st.success(f"Fetched {len(emails)} emails from Gmail!")

                        if emails:
                            try:
                                llm_client = LLMClient()
                                processor = EmailProcessor(llm_client)

                                with st.spinner("Processing emails..."):
                                    for email in emails[:10]:
                                        result = processor.process_email(email)
                                        for task in result["tasks"]:
                                            add_task(task)
                                        for event in result["events"]:
                                            add_event(event)

                                st.success("Emails processed!")
                            except Exception as e:
                                st.warning(f"Could not process emails: {e}")
                    else:
                        st.error("Failed to authenticate with Gmail. Check credentials.")

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
            "Settings": "settings",
        }

        current_page = st.session_state.get("page", "dashboard")
        page_names = list(pages.keys())
        page_values = list(pages.values())

        try:
            current_index = page_values.index(current_page)
        except ValueError:
            current_index = 0

        selected = st.radio(
            "Navigation",
            page_names,
            index=current_index,
            label_visibility="collapsed",
        )

        st.session_state.page = pages[selected]

        st.divider()

        # Quick stats
        st.markdown("### Quick Stats")
        unread = len([e for e in st.session_state.emails if not e.is_read])
        st.metric("Unread", unread)

        todo_tasks = len([t for t in st.session_state.tasks if t.status == "todo"])
        st.metric("Tasks", todo_tasks)

        upcoming_events = len(
            [e for e in st.session_state.events if e.status == "confirmed"]
        )
        st.metric("Events", upcoming_events)

        st.divider()

        # Mode indicator (kept for clarity)
        mode_text = "Mock" if st.session_state.mode == "mock" else "Gmail API"
        st.caption(f"Mode: {mode_text}")
