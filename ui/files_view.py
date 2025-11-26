"""
Files view - Attachments hub.
"""
import streamlit as st
from core.models import Email
from core.state import get_email


def render_files():
    """Render the files/attachments view."""
    st.header("📎 Attachments Hub")
    
    # Get all emails with attachments
    emails_with_attachments = [e for e in st.session_state.emails if e.has_attachments]
    
    if not emails_with_attachments:
        st.info("No emails with attachments found.")
        return
    
    st.markdown(f"Found **{len(emails_with_attachments)}** email(s) with attachments")
    
    # Filter by file type
    file_types = st.multiselect(
        "Filter by File Type",
        ["PDF", "DOC", "DOCX", "PPT", "PPTX", "XLS", "XLSX", "Image", "Other"],
        default=[]
    )
    
    # Display attachments
    st.divider()
    
    attachment_counter = 0  # Counter to ensure unique keys
    
    for email in emails_with_attachments:
        for att_index, attachment in enumerate(email.attachments):
            att_name = attachment.get('name', 'Unknown')
            att_type = attachment.get('type', 'unknown')
            
            # Check if matches filter
            if file_types:
                matches = False
                for ft in file_types:
                    if ft.lower() in att_type.lower() or ft.lower() in att_name.lower():
                        matches = True
                        break
                if not matches:
                    continue
            
            attachment_counter += 1  # Increment for each displayed attachment
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    # File type icon
                    icon = "📄"
                    if "pdf" in att_type.lower():
                        icon = "📕"
                    elif "word" in att_type.lower() or "document" in att_type.lower():
                        icon = "📘"
                    elif "powerpoint" in att_type.lower() or "presentation" in att_type.lower():
                        icon = "📊"
                    elif "excel" in att_type.lower() or "spreadsheet" in att_type.lower():
                        icon = "📗"
                    elif "image" in att_type.lower():
                        icon = "🖼️"
                    
                    st.markdown(f"### {icon} {att_name}")
                    st.caption(f"Type: {att_type}")
                    if attachment.get('size'):
                        size_mb = attachment['size'] / (1024 * 1024)
                        st.caption(f"Size: {size_mb:.2f} MB")
                
                with col2:
                    st.caption(f"**Email:** {email.subject}")
                    st.caption(f"**From:** {email.sender_name}")
                    st.caption(f"**Date:** {email.timestamp.strftime('%Y-%m-%d')}")
                
                with col3:
                    # Use counter and index to ensure unique key
                    unique_key = f"view_file_{attachment_counter}_{email.id}_{att_index}_{hash(att_name) % 10000}"
                    if st.button("View Email", key=unique_key):
                        st.session_state.selected_email_id = email.id
                        st.session_state.page = "inbox"
                        st.rerun()
                
                st.divider()
    
    # Summary statistics
    st.subheader("📊 Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pdf_count = sum(1 for e in emails_with_attachments 
                       for att in e.attachments 
                       if "pdf" in att.get('type', '').lower())
        st.metric("PDF Files", pdf_count)
    
    with col2:
        doc_count = sum(1 for e in emails_with_attachments 
                       for att in e.attachments 
                       if "word" in att.get('type', '').lower() or "document" in att.get('type', '').lower())
        st.metric("Word Documents", doc_count)
    
    with col3:
        image_count = sum(1 for e in emails_with_attachments 
                         for att in e.attachments 
                         if "image" in att.get('type', '').lower())
        st.metric("Images", image_count)

