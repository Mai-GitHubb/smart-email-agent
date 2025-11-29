"""
Tasks view - Kanban board for tasks.
"""
import streamlit as st
from core.state import get_tasks_by_status, update_task_status
from ui.components import task_card
from core.models import Task


def render_tasks():
    """Render the tasks Kanban board."""
    st.header("Task Board")
    
    # Section: Task Statistics
    with st.container():
        st.markdown("### Task Statistics")
        col1, col2, col3 = st.columns(3)
    
    todo_tasks = get_tasks_by_status("todo")
    in_progress_tasks = get_tasks_by_status("in_progress")
    done_tasks = get_tasks_by_status("done")
    
    with col1:
        st.metric("To Do", len(todo_tasks))
    with col2:
        st.metric("In Progress", len(in_progress_tasks))
    with col3:
        st.metric("Done", len(done_tasks))
    
    st.divider()
    
    # Section: Kanban Board
    st.markdown("### Kanban Board")
    st.caption("Drag tasks between columns or use the status dropdown to update task status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("To Do")
        for task in todo_tasks:
            with st.container():
                task_card(task)
                
                # Status change dropdown
                new_status = st.selectbox(
                    "Status",
                    ["todo", "in_progress", "done"],
                    index=0,
                    key=f"status_{task.task_id}"
                )
                
                if new_status != task.status:
                    update_task_status(task.task_id, new_status)
                    st.rerun()
                
                # View source email
                if st.button("View Source Email", key=f"view_{task.task_id}"):
                    st.session_state.selected_email_id = task.source_email_id
                    st.session_state.page = "inbox"
                    st.rerun()
                
                st.divider()
    
    with col2:
        st.subheader("In Progress")
        for task in in_progress_tasks:
            with st.container():
                task_card(task)
                
                new_status = st.selectbox(
                    "Status",
                    ["todo", "in_progress", "done"],
                    index=1,
                    key=f"status_{task.task_id}"
                )
                
                if new_status != task.status:
                    update_task_status(task.task_id, new_status)
                    st.rerun()
                
                if st.button("View Source Email", key=f"view_{task.task_id}"):
                    st.session_state.selected_email_id = task.source_email_id
                    st.session_state.page = "inbox"
                    st.rerun()
                
                st.divider()
    
    with col3:
        st.subheader("Done")
        for task in done_tasks:
            with st.container():
                task_card(task)
                
                new_status = st.selectbox(
                    "Status",
                    ["todo", "in_progress", "done"],
                    index=2,
                    key=f"status_{task.task_id}"
                )
                
                if new_status != task.status:
                    update_task_status(task.task_id, new_status)
                    st.rerun()
                
                if st.button("View Source Email", key=f"view_{task.task_id}"):
                    st.session_state.selected_email_id = task.source_email_id
                    st.session_state.page = "inbox"
                    st.rerun()
                
                st.divider()
    
    # Section: Filters
    st.divider()
    st.markdown("### Filter Tasks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        filter_priority = st.selectbox(
            "Filter by Priority",
            ["All", "High", "Medium", "Low"]
        )
    
    with col2:
        filter_due = st.selectbox(
            "Filter by Due Date",
            ["All", "Overdue", "Due Today", "Due This Week", "Due Later"]
        )

