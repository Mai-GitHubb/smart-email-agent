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
    st.header("📧 Inbox")
    
    # Filters
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
    
    # Email list
    st.subheader(f"Emails ({len(filtered_emails)})")
    
    if not filtered_emails:
        st.info("No emails to display.")
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
    
    # Email detail view
    if st.session_state.selected_email_id:
        render_email_detail(st.session_state.selected_email_id)


def render_email_detail(email_id: str):
    """Render detailed view of a single email."""
    email = get_email(email_id)
    if not email:
        st.error("Email not found.")
        return
    
    st.divider()
    st.header("📧 Email Details")
    
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
    
    # Email body
    st.subheader("Body")
    st.text_area("", email.body, height=200, disabled=True, key=f"body_{email_id}")
    
    # Attachments
    if email.has_attachments:
        st.subheader("📎 Attachments")
        for att in email.attachments:
            st.markdown(f"- {att.get('name', 'Unknown')} ({att.get('type', 'unknown type')})")
    
    # Tabs for actions
    tab1, tab2, tab3, tab4 = st.tabs(["Reply", "Explain", "Set Reminder", "Sender Context"])
    
    with tab1:
        render_reply_tab(email)
    
    with tab2:
        render_explain_tab(email)
    
    with tab3:
        render_reminder_tab(email)
    
    with tab4:
        render_sender_context_tab(email)


def render_reply_tab(email: Email):
    """Render reply generation tab."""
    st.subheader("✍️ Generate Draft Reply")
    
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
    st.subheader("🤔 Why was this email categorized this way?")
    
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
    st.subheader("⏰ Set Reminder")
    
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
    st.subheader("👤 Sender Context")
    
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

