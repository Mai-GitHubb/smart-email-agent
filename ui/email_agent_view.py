import streamlit as st
from core.state import get_email
from core.llm_client import LLMClient
from core import prompts
from core.models import Email


def render_email_agent():
    """Render the Email Agent chat interface."""
    st.header("Email Agent")
    st.caption("Select an email and ask questions. The agent will analyze the email content and provide answers.")
    
    # Email selection
    emails = st.session_state.get('emails', [])
    
    if not emails:
        st.info("No emails available. Load an inbox first.")
        return
    
    # Email selector
    email_options = {f"{e.subject[:50]}... - {e.sender_name}": e.id for e in emails}
    if not email_options:
        email_options = {f"{e.subject} - {e.sender_name}": e.id for e in emails}
    
    selected_email_label = st.selectbox(
        "Select Email",
        list(email_options.keys()),
        key="email_agent_email_selector"
    )
    selected_email_id = email_options[selected_email_label]
    selected_email = get_email(selected_email_id)
    
    if not selected_email:
        st.error("Email not found.")
        return
    
    # Display selected email info
    st.divider()
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Subject:** {selected_email.subject}")
            st.caption(f"From: {selected_email.sender_name} ({selected_email.sender})")
            st.caption(f"Date: {selected_email.timestamp.strftime('%Y-%m-%d %H:%M')}")
            if selected_email.category:
                st.caption(f"Category: {selected_email.category} | Priority: {selected_email.priority or 'Medium'}")
        with col2:
            if st.button("View Full Email", key="view_full_email_agent"):
                st.session_state.selected_email_id = selected_email_id
                st.session_state.page = "inbox"
                st.rerun()
    
    st.divider()
    
    # Example queries
    st.markdown("**Example queries:**")
    example_queries = [
        "Summarize this email",
        "What tasks do I need to do?",
        "What is the deadline?",
        "Who are the participants?",
        "What action items are mentioned?",
        "Draft a reply based on my tone"
    ]
    
    cols = st.columns(3)
    for i, example in enumerate(example_queries):
        with cols[i % 3]:
            if st.button(example, key=f"example_query_{i}"):
                # 🔹 Store query AND mark that we should run it
                st.session_state[f"email_agent_query_{selected_email_id}"] = example
                st.session_state[f"email_agent_run_{selected_email_id}"] = True
                st.rerun()
    
    st.divider()
    
    # Query input (pre-filled from session_state)
    query_key = f"email_agent_query_{selected_email_id}"
    run_flag_key = f"email_agent_run_{selected_email_id}"

    query = st.text_input(
        "Ask a question about this email:",
        value=st.session_state.get(query_key, ""),
        key=f"email_agent_input_{selected_email_id}",
        placeholder="e.g., 'Summarize this email' or 'What tasks do I need to do?'"
    )

    # 🔹 Decide whether to run: either Ask button OR example-click run flag
    ask_clicked = st.button("Ask Agent", key=f"ask_agent_button_{selected_email_id}", type="primary")
    run_from_example = st.session_state.get(run_flag_key, False)

    run_agent = ask_clicked or run_from_example

    # Clear the run flag so it doesn’t keep re-firing
    if run_from_example:
        st.session_state[run_flag_key] = False

    if run_agent:
        if query:
            try:
                llm_client = LLMClient()
                
                # Build context for this specific email
                context_prompt = f"""You are an email assistant. The user has selected a specific email and asked: "{query}"

Email Details:
From: {selected_email.sender_name} ({selected_email.sender})
Subject: {selected_email.subject}
Date: {selected_email.timestamp.strftime('%Y-%m-%d %H:%M')}
Category: {selected_email.category or 'Uncategorized'}
Priority: {selected_email.priority or 'Medium'}

Email Body:
{selected_email.body}

Extracted Information:
"""
                
                # Add tasks and events for this email
                tasks = [t for t in st.session_state.tasks if t.source_email_id == selected_email.id]
                events = [e for e in st.session_state.events if e.source_email_id == selected_email.id]
                
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
                    prompt = st.session_state.prompts.get('reply_generation', prompts.REPLY_GENERATION_PROMPT)
                    tone = "Professional"  # Default tone
                    draft_reply = llm_client.generate_reply(selected_email, "", tone, prompt)
                    st.text_area("Draft Reply", draft_reply, height=200, key=f"agent_draft_{selected_email_id}")
                    
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
        else:
            st.warning("Please enter a question.")
    
    # Chat history (optional - can be enhanced)
    if 'email_agent_history' not in st.session_state:
        st.session_state.email_agent_history = {}
    
    if selected_email_id in st.session_state.email_agent_history:
        st.divider()
        st.markdown("### Previous Queries")
        for prev_query, prev_response in st.session_state.email_agent_history[selected_email_id][-3:]:
            with st.expander(f"Q: {prev_query[:50]}..."):
                st.markdown(prev_response)
