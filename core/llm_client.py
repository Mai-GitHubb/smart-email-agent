"""
LLM Client abstraction layer.

Provides a unified interface for calling different LLM providers (Ollama, OpenAI, Anthropic, etc.).
"""
import json
import os
from typing import List, Dict, Any, Optional
import config
from core.models import Email, Task, Event, CategoryResult

# Import providers conditionally
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMClient:
    """Abstract LLM client for making LLM API calls."""
    
    def __init__(self, provider: str = None, api_key: str = None, model: str = None, base_url: str = None):
        """
        Initialize the LLM client.
        
        Args:
            provider: LLM provider name (defaults to config.LLM_PROVIDER)
            api_key: API key for the provider (defaults to config)
            model: Model name to use (defaults to config)
            base_url: Base URL for Ollama (defaults to config)
        """
        self.provider = provider or config.LLM_PROVIDER
        self.api_key = api_key or getattr(config, 'OPENAI_API_KEY', '')
        self.model = model or config.LLM_MODEL
        self.base_url = base_url or getattr(config, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        
        if self.provider == "ollama":
            if not OLLAMA_AVAILABLE:
                raise ValueError("Ollama package not installed. Install it with: pip install ollama")
            # Test connection by trying to list models (optional check, won't fail if model not found)
            try:
                models_response = ollama.list()
                # Check if the specified model is available
                if models_response and 'models' in models_response:
                    model_names = [m.get('name', '') for m in models_response['models']]
                    if self.model not in model_names:
                        print(f"Warning: Model '{self.model}' not found. Available models: {model_names}")
                        print(f"To install: ollama pull {self.model}")
            except Exception as e:
                # Don't fail initialization if we can't list models, just warn
                print(f"Warning: Could not verify Ollama connection: {str(e)}")
                print("Make sure Ollama is running. The model will be pulled automatically if needed.")
        elif self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ValueError("OpenAI package not installed. Install it with: pip install openai")
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Supported: 'ollama', 'openai'")
    
    def _call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Make a call to the LLM.
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature (0.0-2.0)
            
        Returns:
            The LLM response text
        """
        if self.provider == "ollama":
            try:
                system_message = "You are a helpful email assistant. Always respond with valid JSON when requested."
                
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    options={
                        "temperature": temperature,
                    }
                )
                return response['message']['content']
            except Exception as e:
                raise Exception(f"Ollama API call failed: {str(e)}. Make sure Ollama is running and the model '{self.model}' is installed.")
        elif self.provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful email assistant. Always respond with valid JSON when requested."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"} if "JSON" in prompt.upper() else None
                )
                return response.choices[0].message.content
            except Exception as e:
                raise Exception(f"OpenAI API call failed: {str(e)}")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def categorize_email(self, email: Email, prompt_template: str) -> CategoryResult:
        """
        Categorize an email using the LLM.
        
        Args:
            email: The email to categorize
            prompt_template: The prompt template string
            
        Returns:
            CategoryResult with category, priority, etc.
        """
        prompt = prompt_template.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:2000]  # Limit body length
        )
        
        try:
            response = self._call_llm(prompt)
            # Try to parse JSON response
            if response.strip().startswith("```"):
                # Remove markdown code blocks if present
                response = response.strip().strip("```json").strip("```").strip()
            
            result = json.loads(response)
            return CategoryResult(
                category=result.get("category", "Other"),
                priority=result.get("priority", "Medium"),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning")
            )
        except Exception as e:
            # Fallback to default categorization
            return CategoryResult(
                category="Other",
                priority="Medium",
                confidence=0.0,
                reasoning=f"Error during categorization: {str(e)}"
            )
    
    def extract_tasks(self, email: Email, prompt_template: str) -> List[Task]:
        """
        Extract tasks from an email.
        
        Args:
            email: The email to analyze
            prompt_template: The prompt template string
            
        Returns:
            List of extracted Task objects
        """
        prompt = prompt_template.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:2000],
            email_id=email.id
        )
        
        try:
            response = self._call_llm(prompt)
            # Clean response
            if response.strip().startswith("```"):
                response = response.strip().strip("```json").strip("```").strip()
            
            tasks_data = json.loads(response)
            if not isinstance(tasks_data, list):
                tasks_data = [tasks_data] if tasks_data else []
            
            tasks = []
            for task_data in tasks_data:
                tasks.append(Task(
                    task_id=task_data.get("task_id", f"task_{email.id}_{len(tasks)}"),
                    title=task_data.get("title", ""),
                    due_date=task_data.get("due_date"),
                    source_email_id=email.id,
                    status=task_data.get("status", "todo"),
                    notes=task_data.get("notes"),
                    priority=task_data.get("priority")
                ))
            
            return tasks
        except Exception as e:
            return []  # Return empty list on error
    
    def extract_events(self, email: Email, prompt_template: str) -> List[Event]:
        """
        Extract events and deadlines from an email.
        
        Args:
            email: The email to analyze
            prompt_template: The prompt template string
            
        Returns:
            List of extracted Event objects
        """
        prompt = prompt_template.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:2000],
            email_id=email.id
        )
        
        try:
            response = self._call_llm(prompt)
            # Clean response
            if response.strip().startswith("```"):
                response = response.strip().strip("```json").strip("```").strip()
            
            events_data = json.loads(response)
            if not isinstance(events_data, list):
                events_data = [events_data] if events_data else []
            
            events = []
            for event_data in events_data:
                events.append(Event(
                    event_id=event_data.get("event_id", f"event_{email.id}_{len(events)}"),
                    type=event_data.get("type", "meeting"),
                    title=event_data.get("title", ""),
                    date=event_data.get("date", ""),
                    start_time=event_data.get("start_time"),
                    end_time=event_data.get("end_time"),
                    all_day=event_data.get("all_day", False),
                    location=event_data.get("location"),
                    participants=event_data.get("participants", []),
                    source_email_id=email.id,
                    confidence=event_data.get("confidence", 0.5)
                ))
            
            return events
        except Exception as e:
            return []  # Return empty list on error
    
    def generate_reply(self, email: Email, user_instructions: str, tone: str, prompt_template: str) -> str:
        """
        Generate a draft reply to an email.
        
        Args:
            email: The original email
            user_instructions: Optional user instructions
            tone: Desired tone (Formal, Friendly, Concise, etc.)
            prompt_template: The prompt template string
            
        Returns:
            Generated reply text
        """
        prompt = prompt_template.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:2000],
            user_instructions=user_instructions or "No specific instructions",
            tone=tone
        )
        
        try:
            response = self._call_llm(prompt, temperature=0.7)
            return response.strip()
        except Exception as e:
            return f"Error generating reply: {str(e)}"
    
    def explain_decision(self, email: Email, category: str, priority: str, 
                        tasks: List[Task], events: List[Event], prompt_template: str) -> str:
        """
        Generate an explanation for categorization and extraction decisions.
        
        Args:
            email: The email
            category: Assigned category
            priority: Assigned priority
            tasks: Extracted tasks
            events: Extracted events
            prompt_template: The prompt template string
            
        Returns:
            Explanation text
        """
        tasks_str = ", ".join([t.title for t in tasks]) if tasks else "None"
        events_str = ", ".join([e.title for e in events]) if events else "None"
        
        prompt = prompt_template.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:1000],
            category=category,
            priority=priority,
            tasks=tasks_str,
            events=events_str
        )
        
        try:
            response = self._call_llm(prompt, temperature=0.5)
            return response.strip()
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    def check_reply_tone(self, email: Email, draft_reply: str, requested_tone: str, prompt_template: str) -> Dict[str, Any]:
        """
        Check the tone and completeness of a draft reply.
        
        Args:
            email: Original email
            draft_reply: The draft reply to check
            requested_tone: The requested tone
            prompt_template: The prompt template string
            
        Returns:
            Dictionary with feedback and suggestions
        """
        prompt = prompt_template.format(
            sender=email.sender,
            subject=email.subject,
            original_body=email.body[:1000],
            draft_reply=draft_reply,
            requested_tone=requested_tone
        )
        
        try:
            response = self._call_llm(prompt)
            # Clean response
            if response.strip().startswith("```"):
                response = response.strip().strip("```json").strip("```").strip()
            
            return json.loads(response)
        except Exception as e:
            return {
                "tone_appropriate": False,
                "is_polite": True,
                "all_questions_answered": False,
                "feedback": f"Error checking reply: {str(e)}",
                "suggestions": []
            }
    
    def get_sender_context(self, sender_name: str, sender_email: str, recent_emails: List[Email], prompt_template: str) -> str:
        """
        Generate context about a sender based on recent emails.
        
        Args:
            sender_name: Sender's name
            sender_email: Sender's email
            recent_emails: List of recent emails from this sender
            prompt_template: The prompt template string
            
        Returns:
            Context summary text
        """
        emails_text = "\n\n".join([
            f"Subject: {e.subject}\nBody: {e.body[:200]}"
            for e in recent_emails[:5]
        ])
        
        prompt = prompt_template.format(
            sender_name=sender_name,
            sender_email=sender_email,
            recent_emails=emails_text
        )
        
        try:
            response = self._call_llm(prompt, temperature=0.5)
            return response.strip()
        except Exception as e:
            return f"Error generating context: {str(e)}"
    
    def process_inbox_query(self, query: str, context: Dict[str, Any], prompt_template: str) -> str:
        """
        Process a natural language query about the inbox.
        
        Args:
            query: User's query
            context: Dictionary with inbox context (emails, tasks, events, etc.)
            prompt_template: The prompt template string
            
        Returns:
            Response to the query
        """
        prompt = prompt_template.format(
            query=query,
            total_emails=context.get("total_emails", 0),
            unread_count=context.get("unread_count", 0),
            categories=context.get("categories", ""),
            tasks_summary=context.get("tasks_summary", ""),
            events_summary=context.get("events_summary", "")
        )
        
        try:
            response = self._call_llm(prompt, temperature=0.6)
            return response.strip()
        except Exception as e:
            return f"Error processing query: {str(e)}"

