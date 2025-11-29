"""
Inbox view - Email list and detail view.
"""
import streamlit as st
from core.state import get_email, get_emails_by_category, get_emails_by_sender
from core.models import Email
from ui.components import email_card, category_icon, priority_badge
from core.llm_client import LLMClient
from core.processors import EmailProcessor
from core import prompts
import config


def render_inbox():
    """Render the inbox view."""
    st.header("Inbox")
    
    # Section: Filters
    with st.container():
        st.markdown("### Filter Emails")
        col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All"] + list(set([e.category for e in st.session_state.emails if e.category]))
        )
    
    with col2:
        filter_priority = st.selectbox(
            "Filter by Priority",
            ["All", "High", "Medium", "Low"]
        )
    
    with col3:
        filter_read = st.selectbox(
            "Filter by Status",
            ["All", "Unread", "Read"]
        )
    
    # Apply filters
    filtered_emails = st.session_state.emails.copy()
    
    if filter_category != "All":
        filtered_emails = [e for e in filtered_emails if e.category == filter_category]
    
    if filter_priority != "All":
        filtered_emails = [e for e in filtered_emails if e.priority == filter_priority]
    
    if filter_read == "Unread":
        filtered_emails = [e for e in filtered_emails if not e.is_read]
    elif filter_read == "Read":
        filtered_emails = [e for e in filtered_emails if e.is_read]
    
    # Sort by timestamp (newest first)
    filtered_emails.sort(key=lambda e: e.timestamp, reverse=True)
    
    # Email detail view - show at top if email is selected
    if st.session_state.selected_email_id:
        render_email_detail(st.session_state.selected_email_id)
        st.divider()
        st.subheader("📧 All Emails")
    
    st.divider()
    
    # Section: Email List
    st.subheader(f"Emails ({len(filtered_emails)})")
    
    if not filtered_emails:
        st.info("No emails to display. Load an inbox to get started.")
        return
    
    # Display emails
    for email in filtered_emails:
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.markdown(f"## {category_icon(email.category)}")
                st.markdown(priority_badge(email.priority))
            
            with col2:
                st.markdown(f"**{email.subject}**")
                st.caption(f"From: {email.sender_name} ({email.sender})")
                st.caption(f"📅 {email.timestamp.strftime('%Y-%m-%d %H:%M')}")
                if email.category:
                    st.caption(f"Category: {email.category} | Priority: {email.priority}")
            
            with col3:
                if st.button("View", key=f"view_email_{email.id}"):
                    st.session_state.selected_email_id = email.id
                    st.rerun()
            
            st.divider()


def render_email_detail(email_id: str):
    """Render detailed view of a single email."""
    email = get_email(email_id)
    if not email:
        st.error("Email not found.")
        st.session_state.selected_email_id = None
        return
    
    st.header("Email Details")
    
    # Email header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"## {email.subject}")
        st.markdown(f"**From:** {email.sender_name} ({email.sender})")
        st.markdown(f"**Date:** {email.timestamp.strftime('%Y-%m-%d %H:%M')}")
        if email.category:
            st.markdown(f"**Category:** {category_icon(email.category)} {email.category}")
        if email.priority:
            st.markdown(f"**Priority:** {priority_badge(email.priority)} {email.priority}")
    
    with col2:
        if st.button("← Back to Inbox"):
            st.session_state.selected_email_id = None
            st.rerun()
    
    # Email body - make it clearly visible
    st.subheader("Email Body")
    
    if email.body and email.body.strip():
        st.markdown("---")
        # Show body in a readable format
        # Use st.text for plain text to preserve formatting
        st.text(email.body)
        st.markdown("---")
        
        # Also provide text area for copying
        with st.expander("View/Copy Raw Text"):
            st.text_area("", email.body, height=200, key=f"body_text_{email_id}")
    else:
        st.warning("Email body is empty or could not be extracted.")
        st.info("This may happen if the email has no text content or if there was an error extracting the body from Gmail API.")
    
    # Attachments
    if email.has_attachments:
        st.subheader("Attachments")
        for att in email.attachments:
            st.markdown(f"- {att.get('name', 'Unknown')} ({att.get('type', 'unknown type')})")
    
    # Tabs for actions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Email Agent", "Reply", "Explain", "Set Reminder", "Sender Context"])
    
    with tab1:
        render_email_agent_tab(email)
    
    with tab2:
        render_reply_tab(email)
    
    with tab3:
        render_explain_tab(email)
    
    with tab4:
        render_reminder_tab(email)
    
    with tab5:
        render_sender_context_tab(email)


def render_email_agent_tab(email: Email):
    """Render Email Agent tab - ask questions about this specific email."""
    st.subheader("Email Agent - Ask Questions About This Email")
    
    st.markdown("""
    Ask questions about this specific email. The agent will analyze the email content and provide answers.
    """)
    
    # Pre-filled query examples
    example_queries = [
        "Summarize this email",
        "What tasks do I need to do?",
        "What is the deadline?",
        "Who are the participants?",
        "What action items are mentioned?",
        "Draft a reply based on my tone"
    ]
    
    st.markdown("**Example queries:**")
    cols = st.columns(3)
    for i, example in enumerate(example_queries):
        with cols[i % 3]:
            if st.button(example, key=f"example_{email.id}_{i}"):
                st.session_state[f"email_agent_query_{email.id}"] = example
                st.rerun()
    
    # Query input
    query = st.text_input(
        "Ask a question about this email:",
        value=st.session_state.get(f"email_agent_query_{email.id}", ""),
        key=f"email_agent_input_{email.id}",
        placeholder="e.g., 'Summarize this email' or 'What tasks do I need to do?'"
    )
    
    if st.button("Ask Agent", key=f"ask_agent_{email.id}"):
        if query:
            try:
                from core.llm_client import LLMClient
                
                llm_client = LLMClient()
                
                # Build context for this specific email
                context_prompt = f"""You are an email assistant. The user has selected a specific email and asked: "{query}"

Email Details:
From: {email.sender_name} ({email.sender})
Subject: {email.subject}
Date: {email.timestamp.strftime('%Y-%m-%d %H:%M')}
Category: {email.category or 'Uncategorized'}
Priority: {email.priority or 'Medium'}

Email Body:
{email.body}

Extracted Information:
"""
                
                # Add tasks and events for this email
                tasks = [t for t in st.session_state.tasks if t.source_email_id == email.id]
                events = [e for e in st.session_state.events if e.source_email_id == email.id]
                
                if tasks:
                    context_prompt += "\nTasks:\n"
                    for task in tasks:
                        context_prompt += f"- {task.title} (Due: {task.due_date or 'No due date'}, Status: {task.status})\n"
                
                if events:
                    context_prompt += "\nEvents:\n"
                    for event in events:
                        context_prompt += f"- {event.title} ({event.type}) on {event.date}"
                        if event.start_time:
                            context_prompt += f" at {event.start_time}"
                        context_prompt += "\n"
                
                # Use stored prompts if available
                if "draft" in query.lower() or "reply" in query.lower():
                    # Use reply generation prompt
                    prompt_template = st.session_state.prompts.get('reply_generation', prompts.REPLY_GENERATION_PROMPT)
                    context_prompt += f"\nUse the following prompt style for generating replies:\n{prompt_template}\n"
                
                context_prompt += f"""
Based on the email content and extracted information above, answer the user's question: "{query}"

Provide a clear, helpful answer. If the question asks for a summary, provide a concise summary.
If it asks for tasks, list them clearly. If it asks to draft a reply, generate a professional draft reply.
"""
                
                with st.spinner("Analyzing email and thinking..."):
                    response = llm_client._call_llm(context_prompt, temperature=0.7)
                
                st.markdown("### Agent Response:")
                st.info(response)
                
                # If query is about drafting a reply, also show the draft generation
                if "draft" in query.lower() or "reply" in query.lower():
                    st.markdown("---")
                    st.markdown("### Generated Draft:")
                    # Use the reply generation prompt
                    prompt = st.session_state.prompts.get('reply_generation', prompts.REPLY_GENERATION_PROMPT)
                    tone = "Professional"  # Default tone
                    draft_reply = llm_client.generate_reply(email, "", tone, prompt)
                    st.text_area("Draft Reply", draft_reply, height=200, key=f"agent_draft_{email.id}")
                    
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
        else:
            st.warning("Please enter a question.")


def render_reply_tab(email: Email):
    """Render reply generation tab."""
    st.subheader("Generate Draft Reply")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tone = st.selectbox(
            "Select Tone",
            ["Formal", "Friendly", "Concise", "Professional", "Casual"]
        )
    
    with col2:
        user_instructions = st.text_area(
            "Additional Instructions (optional)",
            placeholder="E.g., 'Mention that I'll follow up next week'"
        )
    
    if st.button("Generate Reply"):
        try:
            llm_client = LLMClient()
            prompt = st.session_state.prompts.get('reply_generation', prompts.REPLY_GENERATION_PROMPT)
            
            with st.spinner("Generating reply..."):
                reply = llm_client.generate_reply(email, user_instructions, tone, prompt)
            
            st.text_area("Draft Reply", reply, height=300, key=f"reply_{email.id}")
            
            # Tone check
            if st.button("Check Tone & Completeness"):
                with st.spinner("Checking reply..."):
                    tone_check_prompt = st.session_state.prompts.get('tone_check', prompts.REPLY_TONE_CHECK_PROMPT)
                    feedback = llm_client.check_reply_tone(email, reply, tone, tone_check_prompt)
                    
                    st.subheader("Feedback")
                    st.json(feedback)
                    
                    if feedback.get('suggestions'):
                        st.subheader("Suggestions")
                        for suggestion in feedback['suggestions']:
                            st.markdown(f"- {suggestion}")
        except Exception as e:
            st.error(f"Error generating reply: {e}")


def render_explain_tab(email: Email):
    """Render explanation tab."""
    st.subheader("Why was this email categorized this way?")
    
    if st.button("Generate Explanation"):
        try:
            # Get tasks and events for this email
            tasks = [t for t in st.session_state.tasks if t.source_email_id == email.id]
            events = [e for e in st.session_state.events if e.source_email_id == email.id]
            
            llm_client = LLMClient()
            prompt = st.session_state.prompts.get('explanation', prompts.EXPLANATION_PROMPT)
            
            with st.spinner("Generating explanation..."):
                explanation = llm_client.explain_decision(
                    email, email.category or "Unknown", email.priority or "Medium",
                    tasks, events, prompt
                )
            
            st.markdown(explanation)
        except Exception as e:
            st.error(f"Error generating explanation: {e}")


def render_reminder_tab(email: Email):
    """Render reminder setting tab."""
    st.subheader("Set Reminder")
    
    reminder_options = {
        "Today evening": "today_evening",
        "Tomorrow morning": "tomorrow_morning",
        "Next week": "next_week",
        "Custom": "custom"
    }
    
    selected_option = st.radio("When?", list(reminder_options.keys()))
    
    reminder_time = None
    if selected_option == "custom":
        reminder_time = st.datetime_input("Select Date & Time")
    else:
        from datetime import datetime, timedelta
        now = datetime.now()
        if selected_option == "today_evening":
            reminder_time = now.replace(hour=18, minute=0)
        elif selected_option == "tomorrow_morning":
            reminder_time = (now + timedelta(days=1)).replace(hour=9, minute=0)
        elif selected_option == "next_week":
            reminder_time = now + timedelta(days=7)
    
    note = st.text_area("Reminder Note", placeholder="Optional note about this reminder")
    
    if st.button("Set Reminder") and reminder_time:
        from core.models import Reminder
        import uuid
        
        reminder = Reminder(
            id=str(uuid.uuid4()),
            email_id=email.id,
            reminder_time=reminder_time,
            note=note or f"Reminder for: {email.subject}",
            status="pending"
        )
        
        from core.state import add_reminder
        add_reminder(reminder)
        st.success("Reminder set!")


def render_sender_context_tab(email: Email):
    """Render sender context tab."""
    st.subheader("Sender Context")
    
    st.markdown(f"**Name:** {email.sender_name}")
    st.markdown(f"**Email:** {email.sender}")
    
    # Get recent emails from this sender
    from core.state import get_emails_by_sender
    recent_emails = get_emails_by_sender(email.sender)
    recent_emails = [e for e in recent_emails if e.id != email.id][:5]
    
    st.subheader("Recent Emails from This Sender")
    if recent_emails:
        for e in recent_emails:
            st.markdown(f"- {e.subject} ({e.timestamp.strftime('%Y-%m-%d')})")
    else:
        st.info("No other emails from this sender.")
    
    if st.button("Generate Context Summary"):
        try:
            llm_client = LLMClient()
            prompt = st.session_state.prompts.get('sender_context', prompts.SENDER_CONTEXT_PROMPT)
            
            with st.spinner("Generating context..."):
                context = llm_client.get_sender_context(
                    email.sender_name, email.sender, recent_emails, prompt
                )
            
            st.subheader("Context Summary")
            st.markdown(context)
        except Exception as e:
            st.error(f"Error generating context: {e}")

