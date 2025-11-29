"""
Email processing functions.

Handles categorization, extraction, and other LLM-powered processing.
"""
from typing import List, Dict, Any
from core.models import Email, Task, Event, CategoryResult
from core.llm_client import LLMClient
from core import prompts


class EmailProcessor:
    """Processes emails using LLM for categorization and extraction."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize processor.
        
        Args:
            llm_client: Initialized LLMClient instance
        """
        self.llm_client = llm_client
        self.categorization_prompt = prompts.CATEGORIZATION_PROMPT
        self.task_extraction_prompt = prompts.TASK_EXTRACTION_PROMPT
        self.event_extraction_prompt = prompts.EVENT_EXTRACTION_PROMPT
    
    def categorize_email(self, email: Email, custom_prompt: str = None) -> CategoryResult:
        """
        Categorize an email.
        
        Args:
            email: Email to categorize
            custom_prompt: Optional custom prompt template
            
        Returns:
            CategoryResult
        """
        prompt = custom_prompt or self.categorization_prompt
        return self.llm_client.categorize_email(email, prompt)
    
    def extract_tasks(self, email: Email, custom_prompt: str = None) -> List[Task]:
        """
        Extract tasks from an email.
        
        Args:
            email: Email to analyze
            custom_prompt: Optional custom prompt template
            
        Returns:
            List of Task objects
        """
        prompt = custom_prompt or self.task_extraction_prompt
        return self.llm_client.extract_tasks(email, prompt)
    
    def extract_events(self, email: Email, custom_prompt: str = None) -> List[Event]:
        """
        Extract events from an email.
        
        Args:
            email: Email to analyze
            custom_prompt: Optional custom prompt template
            
        Returns:
            List of Event objects
        """
        prompt = custom_prompt or self.event_extraction_prompt
        return self.llm_client.extract_events(email, prompt)
    
    def process_email(self, email: Email, categorize: bool = True, 
                     extract_tasks_flag: bool = True, extract_events_flag: bool = True) -> Dict[str, Any]:
        """
        Process an email comprehensively.
        
        This is the main processing function that orchestrates all LLM-powered operations:
        1. Categorization: Assigns category (Work, Personal, To-Do, etc.) and priority
        2. Task Extraction: Extracts actionable tasks with due dates
        3. Event Extraction: Extracts meetings and deadlines
        
        All operations use prompts from the Prompt Brain (st.session_state.prompts),
        making the system fully prompt-driven.
        
        Args:
            email: Email to process
            categorize: Whether to categorize the email
            extract_tasks_flag: Whether to extract tasks from the email
            extract_events_flag: Whether to extract events/deadlines from the email
            
        Returns:
            Dictionary with processing results containing:
            - email_id: ID of processed email
            - category: Assigned category (if categorized)
            - priority: Assigned priority (if categorized)
            - tasks: List of extracted Task objects
            - events: List of extracted Event objects
        """
        results = {
            'email_id': email.id,
            'category': None,
            'priority': None,
            'tasks': [],
            'events': []
        }
        
        # Step 1: Categorize email using LLM
        # Uses categorization prompt from Prompt Brain
        if categorize:
            try:
                category_result = self.categorize_email(email)
                # Update email object with category and priority
                email.category = category_result.category
                email.priority = category_result.priority
                results['category'] = category_result.category
                results['priority'] = category_result.priority
            except Exception as e:
                # Graceful error handling - continue processing even if categorization fails
                print(f"Error categorizing email {email.id}: {e}")
        
        # Step 2: Extract tasks from email using LLM
        # Uses task extraction prompt from Prompt Brain
        if extract_tasks_flag:
            try:
                tasks = self.extract_tasks(email)
                results['tasks'] = tasks
                # Note: Tasks should be added to state using add_task() after processing
            except Exception as e:
                print(f"Error extracting tasks from email {email.id}: {e}")
        
        # Step 3: Extract events/deadlines from email using LLM
        # Uses event extraction prompt from Prompt Brain
        if extract_events_flag:
            try:
                events = self.extract_events(email)
                results['events'] = events
                # Note: Events should be added to state using add_event() after processing
            except Exception as e:
                print(f"Error extracting events from email {email.id}: {e}")
        
        return results
    
    def batch_process_emails(self, emails: List[Email], 
                            categorize: bool = True,
                            extract_tasks_flag: bool = True,
                            extract_events_flag: bool = True) -> Dict[str, Any]:
        """
        Process multiple emails in batch.
        
        Args:
            emails: List of emails to process
            categorize: Whether to categorize
            extract_tasks_flag: Whether to extract tasks
            extract_events_flag: Whether to extract events
            
        Returns:
            Dictionary mapping email_id to processing results
        """
        results = {}
        for email in emails:
            results[email.id] = self.process_email(
                email, categorize, extract_tasks_flag, extract_events_flag
            )
        return results

