"""
Drafts view - Manage email drafts (replies and new emails).
"""
import streamlit as st
from datetime import datetime
from core.models import Draft
from core.llm_client import LLMClient
from core import prompts
import uuid


def render_drafts():
    """Render the drafts management view."""
    st.header("Email Drafts")
    st.caption("Create, edit, and manage your email drafts")
    
    # Tabs for different draft types
    tab1, tab2 = st.tabs(["Saved Drafts", "Create New Draft"])
    
    with tab1:
        render_saved_drafts()
    
    with tab2:
        render_new_draft()


def render_saved_drafts():
    """Render list of saved drafts."""
    drafts = st.session_state.get('drafts', [])
    
    if not drafts:
        st.info("No saved drafts. Create a new draft to get started.")
        return
    
    st.subheader(f"Saved Drafts ({len(drafts)})")
    
    for draft in reversed(drafts):  # Show newest first
        with st.expander(f"📧 {draft.subject} - {draft.created_at.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**To:** {draft.recipient or 'Not specified'}")
                st.markdown(f"**Tone:** {draft.tone}")
                if draft.reply_to_email_id:
                    st.caption(f"Reply to email: {draft.reply_to_email_id}")
            
            with col2:
                if st.button("Edit", key=f"edit_{draft.id}"):
                    st.session_state.editing_draft_id = draft.id
                    st.rerun()
                
                if st.button("Delete", key=f"delete_{draft.id}"):
                    st.session_state.drafts = [d for d in st.session_state.drafts if d.id != draft.id]
                    st.rerun()
            
            st.text_area("Body", draft.body, height=200, key=f"body_{draft.id}", disabled=True)
            
            if draft.suggested_followups:
                st.markdown("**Suggested Follow-ups:**")
                for followup in draft.suggested_followups:
                    st.markdown(f"- {followup}")
            
            if draft.metadata:
                with st.expander("Metadata"):
                    st.json(draft.metadata)


def render_new_draft():
    """Render new draft creation interface."""
    st.subheader("Create New Email Draft")
    
    draft_type = st.radio(
        "Draft Type",
        ["New Email", "Reply to Email"],
        horizontal=True
    )
    
    if draft_type == "Reply to Email":
        # Show email selector
        emails = st.session_state.get('emails', [])
        if not emails:
            st.warning("No emails available. Load an inbox first.")
            return
        
        email_options = {f"{e.subject} - {e.sender_name}": e.id for e in emails}
        selected_email_label = st.selectbox("Select Email to Reply To", list(email_options.keys()))
        selected_email_id = email_options[selected_email_label]
        
        # Get the email
        from core.state import get_email
        email = get_email(selected_email_id)
        
        if email:
            st.markdown(f"**Replying to:** {email.subject}")
            st.markdown(f"**From:** {email.sender_name} ({email.sender})")
            
            # Pre-fill recipient
            recipient = st.text_input("To", value=email.sender)
            subject = st.text_input("Subject", value=f"Re: {email.subject}")
    else:
        recipient = st.text_input("To", placeholder="recipient@example.com")
        subject = st.text_input("Subject", placeholder="Email subject")
        email = None
        selected_email_id = None
    
    # Common fields
    col1, col2 = st.columns(2)
    
    with col1:
        tone = st.selectbox(
            "Tone",
            ["Formal", "Friendly", "Concise", "Professional", "Casual"]
        )
    
    with col2:
        user_requirements = st.text_area(
            "What should this email say?",
            placeholder="Describe what you want to communicate...",
            height=100
        )
    
    if st.button("Generate Draft", type="primary"):
        if not recipient or not subject or not user_requirements:
            st.error("Please fill in all required fields.")
            return
        
        try:
            llm_client = LLMClient()
            
            if draft_type == "Reply to Email" and email:
                # Use reply generation prompt
                prompt = st.session_state.prompts.get('reply_generation', prompts.REPLY_GENERATION_PROMPT)
                
                with st.spinner("Generating reply..."):
                    body = llm_client.generate_reply(
                        email, user_requirements, tone, prompt
                    )
            else:
                # Use new draft generation prompt
                prompt = st.session_state.prompts.get('new_draft_generation', prompts.NEW_DRAFT_GENERATION_PROMPT)
                
                with st.spinner("Generating draft..."):
                    formatted_prompt = prompt.format(
                        user_requirements=user_requirements,
                        recipient=recipient,
                        tone=tone,
                        subject=subject
                    )
                    body = llm_client._call_llm(formatted_prompt, temperature=0.7)
            
            # Generate suggested follow-ups
            followup_prompt = f"""Based on this email draft, suggest 2-3 potential follow-up actions or topics:

Email Subject: {subject}
Email Body: {body}

Provide 2-3 brief follow-up suggestions as a JSON array:
["suggestion1", "suggestion2", "suggestion3"]

Only return the JSON array."""
            
            try:
                followup_response = llm_client._call_llm(followup_prompt, temperature=0.6)
                import json
                if followup_response.strip().startswith("```"):
                    followup_response = followup_response.strip().strip("```json").strip("```").strip()
                parsed = json.loads(followup_response)
                
                # Handle different response formats
                if isinstance(parsed, list):
                    # Extract strings from list (handle both string lists and dict lists)
                    suggested_followups = []
                    for item in parsed:
                        if isinstance(item, str):
                            suggested_followups.append(item)
                        elif isinstance(item, dict):
                            # If it's a dict, try to extract the suggestion text
                            if "suggestion" in item:
                                suggested_followups.append(str(item["suggestion"]))
                            elif "text" in item:
                                suggested_followups.append(str(item["text"]))
                            elif "followup" in item:
                                suggested_followups.append(str(item["followup"]))
                            else:
                                # Take first string value
                                for val in item.values():
                                    if isinstance(val, str):
                                        suggested_followups.append(val)
                                        break
                else:
                    suggested_followups = []
            except Exception as e:
                print(f"Error parsing follow-ups: {e}")
                suggested_followups = []
            
            # Create draft
            draft = Draft(
                id=str(uuid.uuid4()),
                subject=subject,
                body=body,
                recipient=recipient,
                reply_to_email_id=selected_email_id,
                tone=tone,
                created_at=datetime.now(),
                metadata={
                    "type": "reply" if draft_type == "Reply to Email" else "new",
                    "category": email.category if email else None,
                    "priority": email.priority if email else None
                },
                suggested_followups=suggested_followups,
                status="draft"
            )
            
            # Add to drafts
            if 'drafts' not in st.session_state:
                st.session_state.drafts = []
            st.session_state.drafts.append(draft)
            
            st.success("Draft generated and saved!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating draft: {str(e)}")
    
    # Show editing interface if editing
    if 'editing_draft_id' in st.session_state:
        draft_to_edit = next((d for d in st.session_state.drafts if d.id == st.session_state.editing_draft_id), None)
        if draft_to_edit:
            st.divider()
            st.subheader("Edit Draft")
            
            edited_subject = st.text_input("Subject", value=draft_to_edit.subject, key="edit_subject")
            edited_body = st.text_area("Body", value=draft_to_edit.body, height=300, key="edit_body")
            edited_recipient = st.text_input("To", value=draft_to_edit.recipient or "", key="edit_recipient")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes"):
                    draft_to_edit.subject = edited_subject
                    draft_to_edit.body = edited_body
                    draft_to_edit.recipient = edited_recipient
                    draft_to_edit.status = "saved"
                    del st.session_state.editing_draft_id
                    st.success("Draft updated!")
                    st.rerun()
            
            with col2:
                if st.button("Cancel"):
                    del st.session_state.editing_draft_id
                    st.rerun()

