# Smart Email Agent - Code Documentation

This document provides detailed documentation for all modules, classes, and functions in the Smart Email Agent codebase.

## Table of Contents

1. [Configuration (`config.py`)](#configuration)
2. [Core Models (`core/models.py`)](#core-models)
3. [LLM Client (`core/llm_client.py`)](#llm-client)
4. [Prompts (`core/prompts.py`)](#prompts)
5. [Processors (`core/processors.py`)](#processors)
6. [Gmail Client (`core/gmail_client.py`)](#gmail-client)
7. [Mock Data Loader (`core/mock_data_loader.py`)](#mock-data-loader)
8. [State Management (`core/state.py`)](#state-management)
9. [UI Components (`ui/components.py`)](#ui-components)
10. [UI Views](#ui-views)
11. [Main Application (`app.py`)](#main-application)

---

## Configuration

**File**: `config.py`

**Purpose**: Centralized configuration and constants.

### Variables

- `LLM_PROVIDER`: LLM provider name (default: "gemini")
- `LLM_MODEL`: Model name to use (default: "gemini-2.5-flash")
- `OPENAI_API_KEY`: OpenAI API key from environment (optional)
- `OPENAI_MODEL`: OpenAI model name (default: "gpt-4-turbo-preview")
- `GMAIL_CREDENTIALS_FILE`: Path to Gmail OAuth credentials
- `GMAIL_TOKEN_FILE`: Path to store Gmail OAuth token
- `GMAIL_SCOPES`: Gmail API scopes (read-only)
- `GOOGLE_CALENDAR_CREDENTIALS_FILE`: Path to Google Calendar OAuth credentials
- `GOOGLE_CALENDAR_TOKEN_FILE`: Path to store Google Calendar OAuth token
- `GOOGLE_CALENDAR_SCOPES`: Google Calendar API scopes
- `APP_TITLE`: Application title
- `APP_ICON`: Application icon emoji
- `DEFAULT_MODE`: Default mode ("mock" or "gmail")
- `DATA_DIR`: Data directory path
- `MOCK_INBOX_FILE`: Path to mock inbox JSON file
- `ITEMS_PER_PAGE`: Pagination size
- `MAX_EMAILS_TO_FETCH`: Maximum emails to fetch from Gmail (default: 100)

---

## Core Models

**File**: `core/models.py`

**Purpose**: Defines data structures using Pydantic for validation.

### Classes

#### `Email`
Represents an email message.

**Fields**:
- `id: str` - Unique email identifier
- `sender: str` - Sender email address
- `sender_name: str` - Sender display name
- `subject: str` - Email subject
- `body: str` - Email body text
- `timestamp: datetime` - Email timestamp
- `labels: List[str]` - Email labels/tags
- `has_attachments: bool` - Whether email has attachments
- `attachments: List[Dict[str, Any]]` - Attachment metadata
- `category: Optional[str]` - Assigned category
- `priority: Optional[str]` - Assigned priority (High/Medium/Low)
- `is_read: bool` - Read status
- `thread_id: Optional[str]` - Thread identifier

#### `Task`
Represents a task extracted from an email.

**Fields**:
- `task_id: str` - Unique task identifier
- `title: str` - Task title/description
- `due_date: Optional[str]` - Due date (YYYY-MM-DD format)
- `source_email_id: str` - ID of source email
- `status: str` - Task status ("todo", "in_progress", "done")
- `notes: Optional[str]` - Additional notes
- `priority: Optional[str]` - Task priority

#### `Event`
Represents an event or deadline extracted from an email.

**Fields**:
- `event_id: str` - Unique event identifier
- `type: str` - Event type ("meeting" or "deadline")
- `title: str` - Event title
- `date: str` - Event date (YYYY-MM-DD format)
- `start_time: Optional[str]` - Start time (HH:MM format)
- `end_time: Optional[str]` - End time (HH:MM format)
- `all_day: bool` - Whether event is all-day
- `location: Optional[str]` - Event location
- `participants: List[str]` - List of participants
- `source_email_id: str` - ID of source email
- `confidence: float` - Extraction confidence (0.0-1.0)
- `status: str` - Event status ("suggested", "confirmed", "ignored")

#### `Reminder`
Represents a reminder linked to an email.

**Fields**:
- `id: str` - Unique reminder identifier
- `email_id: str` - ID of linked email
- `reminder_time: datetime` - When to remind
- `note: str` - Reminder note
- `status: str` - Reminder status ("pending", "done")

#### `Draft`
Represents an email draft (reply or new email).

**Fields**:
- `id: str` - Unique draft identifier
- `subject: str` - Draft subject
- `body: str` - Draft body text
- `recipient: Optional[str]` - Recipient email address
- `reply_to_email_id: Optional[str]` - ID of email being replied to (if applicable)
- `tone: str` - Draft tone (Formal, Friendly, etc.)
- `created_at: datetime` - Creation timestamp
- `metadata: Dict[str, Any]` - JSON metadata (category, priority, type)
- `suggested_followups: List[str]` - AI-generated follow-up suggestions
- `status: str` - Draft status ("draft", "saved", "sent")

#### `CategoryResult`
Result of email categorization.

**Fields**:
- `category: str` - Assigned category
- `priority: str` - Assigned priority
- `confidence: float` - Confidence score
- `reasoning: Optional[str]` - Explanation

---

## LLM Client

**File**: `core/llm_client.py`

**Purpose**: Abstraction layer for LLM API calls.

### Class: `LLMClient`

#### `__init__(provider: str = None, api_key: str = None, model: str = None, base_url: str = None)`
Initialize LLM client.

**Parameters**:
- `provider`: LLM provider name (defaults to config, supports "gemini" or "openai")
- `api_key`: API key for OpenAI (defaults to config, not needed for gemini)
- `model`: Model name (defaults to config, e.g., "gemini-2.5-flash" for gemini)

**Raises**: `ValueError` if provider unsupported or API key missing (for OpenAI)

#### `_call_llm(prompt: str, temperature: float = 0.3) -> str`
Make a call to the LLM.

**Parameters**:
- `prompt`: The prompt text
- `temperature`: Sampling temperature (0.0-2.0)

**Returns**: LLM response text

**Raises**: `Exception` on API failure

#### `categorize_email(email: Email, prompt_template: str) -> CategoryResult`
Categorize an email using LLM.

**Parameters**:
- `email`: Email to categorize
- `prompt_template`: Prompt template string

**Returns**: `CategoryResult` with category, priority, etc.

#### `extract_tasks(email: Email, prompt_template: str) -> List[Task]`
Extract tasks from an email.

**Parameters**:
- `email`: Email to analyze
- `prompt_template`: Prompt template

**Returns**: List of `Task` objects

#### `extract_events(email: Email, prompt_template: str) -> List[Event]`
Extract events from an email.

**Parameters**:
- `email`: Email to analyze
- `prompt_template`: Prompt template

**Returns**: List of `Event` objects

#### `generate_reply(email: Email, user_instructions: str, tone: str, prompt_template: str) -> str`
Generate a draft reply to an email.

**Parameters**:
- `email`: Original email
- `user_instructions`: Optional user instructions
- `tone`: Desired tone (Formal, Friendly, etc.)
- `prompt_template`: Prompt template

**Returns**: Generated reply text

#### `explain_decision(email: Email, category: str, priority: str, tasks: List[Task], events: List[Event], prompt_template: str) -> str`
Generate explanation for categorization/extraction decisions.

**Parameters**:
- `email`: The email
- `category`: Assigned category
- `priority`: Assigned priority
- `tasks`: Extracted tasks
- `events`: Extracted events
- `prompt_template`: Prompt template

**Returns**: Explanation text

#### `check_reply_tone(email: Email, draft_reply: str, requested_tone: str, prompt_template: str) -> Dict[str, Any]`
Check tone and completeness of draft reply.

**Parameters**:
- `email`: Original email
- `draft_reply`: Draft reply text
- `requested_tone`: Requested tone
- `prompt_template`: Prompt template

**Returns**: Dictionary with feedback and suggestions

#### `get_sender_context(sender_name: str, sender_email: str, recent_emails: List[Email], prompt_template: str) -> str`
Generate context about a sender.

**Parameters**:
- `sender_name`: Sender's name
- `sender_email`: Sender's email
- `recent_emails`: Recent emails from sender
- `prompt_template`: Prompt template

**Returns**: Context summary text

#### `process_inbox_query(query: str, context: Dict[str, Any], prompt_template: str) -> str`
Process natural language query about inbox.

**Parameters**:
- `query`: User's query
- `context`: Inbox context dictionary (includes emails_text, tasks_text, events_text)
- `prompt_template`: Prompt template

**Returns**: Response text

**Note**: Reads all emails, tasks, and events to provide comprehensive answers.

#### `generate_new_draft(user_requirements: str, recipient: str, subject: str, tone: str, prompt_template: str) -> str`
Generate a new email draft (not a reply).

**Parameters**:
- `user_requirements`: What the email should say
- `recipient`: Recipient email address
- `subject`: Email subject
- `tone`: Desired tone
- `prompt_template`: Prompt template

**Returns**: Generated draft text

---

## Prompts

**File**: `core/prompts.py`

**Purpose**: Centralized prompt templates.

### Constants

- `CATEGORIZATION_PROMPT`: Email categorization prompt
- `TASK_EXTRACTION_PROMPT`: Task extraction prompt
- `EVENT_EXTRACTION_PROMPT`: Event/deadline extraction prompt
- `REPLY_GENERATION_PROMPT`: Reply generation prompt
- `EXPLANATION_PROMPT`: Explanation prompt
- `REPLY_TONE_CHECK_PROMPT`: Tone check prompt
- `SENDER_CONTEXT_PROMPT`: Sender context prompt
- `INBOX_QUERY_PROMPT`: Inbox query prompt

All prompts use Python string formatting with placeholders like `{sender}`, `{subject}`, etc.

---

## Processors

**File**: `core/processors.py`

**Purpose**: Orchestrates email processing.

### Class: `EmailProcessor`

#### `__init__(llm_client: LLMClient)`
Initialize processor with LLM client.

**Parameters**:
- `llm_client`: Initialized `LLMClient` instance

#### `categorize_email(email: Email, custom_prompt: str = None) -> CategoryResult`
Categorize an email.

**Parameters**:
- `email`: Email to categorize
- `custom_prompt`: Optional custom prompt

**Returns**: `CategoryResult`

#### `extract_tasks(email: Email, custom_prompt: str = None) -> List[Task]`
Extract tasks from email.

**Parameters**:
- `email`: Email to analyze
- `custom_prompt`: Optional custom prompt

**Returns**: List of `Task` objects

#### `extract_events(email: Email, custom_prompt: str = None) -> List[Event]`
Extract events from email.

**Parameters**:
- `email`: Email to analyze
- `custom_prompt`: Optional custom prompt

**Returns**: List of `Event` objects

#### `process_email(email: Email, categorize: bool = True, extract_tasks_flag: bool = True, extract_events_flag: bool = True) -> Dict[str, Any]`
Process email comprehensively.

**Parameters**:
- `email`: Email to process
- `categorize`: Whether to categorize
- `extract_tasks_flag`: Whether to extract tasks
- `extract_events_flag`: Whether to extract events

**Returns**: Dictionary with processing results

#### `batch_process_emails(emails: List[Email], categorize: bool = True, extract_tasks_flag: bool = True, extract_events_flag: bool = True) -> Dict[str, Any]`
Process multiple emails in batch.

**Parameters**:
- `emails`: List of emails
- `categorize`: Whether to categorize
- `extract_tasks_flag`: Whether to extract tasks
- `extract_events_flag`: Whether to extract events

**Returns**: Dictionary mapping email_id to results

---

## Gmail Client

**File**: `core/gmail_client.py`

**Purpose**: Wraps Gmail API for email fetching.

### Class: `GmailClient`

#### `__init__(credentials_file: str = None, token_file: str = None)`
Initialize Gmail client.

**Parameters**:
- `credentials_file`: Path to OAuth credentials JSON
- `token_file`: Path to store/load OAuth token

#### `authenticate() -> bool`
Authenticate with Gmail API using OAuth 2.0.

**Returns**: `True` if successful, `False` otherwise

#### `fetch_emails(max_results: int = 100, query: str = None) -> List[Email]`
Fetch emails from Gmail.

**Parameters**:
- `max_results`: Maximum number of emails
- `query`: Gmail search query (optional)

**Returns**: List of `Email` objects

#### `_fetch_email_details(message_id: str) -> Optional[Email]`
Fetch detailed information for a single email.

**Parameters**:
- `message_id`: Gmail message ID

**Returns**: `Email` object or `None`

#### `_extract_body(payload: dict) -> str`
Extract email body from Gmail payload.

**Parameters**:
- `payload`: Gmail message payload

**Returns**: Email body text (prefers plain text, falls back to HTML with tag stripping)

**Features**:
- Handles nested multipart messages recursively
- Prefers text/plain over text/html
- Strips HTML tags and decodes entities when only HTML is available
- Handles single-part and multipart messages

#### `is_authenticated() -> bool`
Check if client is authenticated.

**Returns**: `True` if authenticated

---

## Mock Data Loader

**File**: `core/mock_data_loader.py`

**Purpose**: Loads sample emails for demo/testing.

### Functions

#### `load_mock_inbox(file_path: str = None) -> List[Email]`
Load mock emails from JSON file.

**Parameters**:
- `file_path`: Path to JSON file (defaults to config)

**Returns**: List of `Email` objects

**Behavior**: If file doesn't exist, generates sample data

#### `_generate_sample_emails() -> List[Email]`
Generate sample emails for demo.

**Returns**: List of sample `Email` objects

**Note**: Internal function, generates 15 sample emails. The actual mock inbox JSON file contains 25 diverse emails.

---

## State Management

**File**: `core/state.py`

**Purpose**: Manages Streamlit session state.

### Functions

#### `initialize_state()`
Initialize all session state variables.

**Sets**:
- `emails`: List of emails
- `tasks`: List of tasks
- `events`: List of events
- `reminders`: List of reminders
- `selected_email_id`: Currently selected email
- `mode`: Current mode ("mock" or "gmail")
- `prompts`: Dictionary of prompt templates
- `processing_cache`: Cache for processing results

#### `get_email(email_id: str) -> Optional[Email]`
Get email by ID.

**Parameters**:
- `email_id`: Email identifier

**Returns**: `Email` object or `None`

#### `add_task(task: Task)`
Add task to state (if not already present).

**Parameters**:
- `task`: Task to add

#### `add_event(event: Event)`
Add event to state (if not already present).

**Parameters**:
- `event`: Event to add

#### `add_reminder(reminder: Reminder)`
Add reminder to state.

**Parameters**:
- `reminder`: Reminder to add

#### `get_tasks_by_status(status: str) -> List[Task]`
Get tasks filtered by status.

**Parameters**:
- `status`: Task status ("todo", "in_progress", "done")

**Returns**: List of matching tasks

#### `get_events_by_date(date: str) -> List[Event]`
Get events for a specific date.

**Parameters**:
- `date`: Date in YYYY-MM-DD format

**Returns**: List of confirmed events for that date

#### `get_upcoming_events(days: int = 7) -> List[Event]`
Get upcoming events within next N days.

**Parameters**:
- `days`: Number of days ahead

**Returns**: Sorted list of upcoming events

#### `get_tasks_due_soon(days: int = 7) -> List[Task]`
Get tasks due within next N days.

**Parameters**:
- `days`: Number of days ahead

**Returns**: Sorted list of due tasks

#### `get_high_priority_emails() -> List[Email]`
Get high priority unread emails.

**Returns**: List of high priority unread emails

#### `get_emails_by_category(category: str) -> List[Email]`
Get emails filtered by category.

**Parameters**:
- `category`: Category name

**Returns**: List of matching emails

#### `get_emails_by_sender(sender_email: str) -> List[Email]`
Get emails from a specific sender.

**Parameters**:
- `sender_email`: Sender email address

**Returns**: List of emails from sender

#### `update_task_status(task_id: str, new_status: str)`
Update a task's status.

**Parameters**:
- `task_id`: Task identifier
- `new_status`: New status

#### `confirm_event(event_id: str)`
Confirm an event (move to confirmed status).

**Parameters**:
- `event_id`: Event identifier

#### `ignore_event(event_id: str)`
Ignore an event.

**Parameters**:
- `event_id`: Event identifier

---

## UI Components

**File**: `ui/components.py`

**Purpose**: Reusable UI components.

### Functions

#### `priority_badge(priority: Optional[str]) -> str`
Get emoji for priority level.

**Parameters**:
- `priority`: Priority level ("High", "Medium", "Low")

**Returns**: Emoji string

#### `category_icon(category: Optional[str]) -> str`
Get emoji for category.

**Parameters**:
- `category`: Category name

**Returns**: Emoji string

#### `email_card(email: Email, show_body: bool = False)`
Display email as a card.

**Parameters**:
- `email`: Email to display
- `show_body`: Whether to show body in expander

#### `task_card(task: Task)`
Display task as a card.

**Parameters**:
- `task`: Task to display

#### `event_card(event: Event, show_actions: bool = False)`
Display event as a card.

**Parameters**:
- `event`: Event to display
- `show_actions`: Whether to show action buttons

**Returns**: Action result string or `None`

#### `info_card(title: str, content: str, icon: str = "ℹ️")`
Display an info card.

**Parameters**:
- `title`: Card title
- `content`: Card content
- `icon`: Icon emoji

#### `stat_card(label: str, value: str, icon: str = "")`
Display a statistics card.

**Parameters**:
- `label`: Metric label
- `value`: Metric value
- `icon`: Icon emoji

---

## UI Views

### Dashboard (`ui/dashboard.py`)

#### `render_dashboard()`
Render the main dashboard view.

**Displays**:
- Statistics row (unread, tasks, events, due soon)
- 2x2 grid layout with styled sections:
  - High priority unread emails (left, top)
  - Upcoming deadlines (left, bottom)
  - Next meetings (right, top)
  - Top tasks (right, bottom)
- Each section has borders, shadows, and proper spacing
- Quick actions to navigate to other pages

### Inbox View (`ui/inbox_view.py`)

#### `render_inbox()`
Render the inbox view with email list and filters.

#### `render_email_detail(email_id: str)`
Render detailed view of a single email.

**Parameters**:
- `email_id`: Email identifier

**Features**:
- Email header and body (clearly visible with markdown formatting)
- Attachments list
- Tabs: Email Agent, Reply, Explain, Set Reminder, Sender Context
- Email Agent tab: Ask questions about the specific email

#### `render_reply_tab(email: Email)`
Render reply generation tab.

#### `render_explain_tab(email: Email)`
Render explanation tab.

#### `render_reminder_tab(email: Email)`
Render reminder setting tab.

#### `render_sender_context_tab(email: Email)`
Render sender context tab.

### Calendar View (`ui/calendar_view.py`)

#### `render_calendar()`
Render the calendar view with tabs and Google Calendar sync options.

#### `render_calendar_view()`
Render calendar month grid view.

**Features**:
- Month/year selector
- Visual grid with tasks and events displayed on their dates
- Todo calendar style layout
- Detail view for selected date
- Uses `date_utils.parse_date()` for robust date parsing

#### `render_suggested_events()`
Render suggested events management.

**Features**:
- List all suggested events from email extraction
- Confirm events (automatically syncs to Google Calendar)
- Edit events (with safe date parsing)
- Ignore events

#### `_sync_tasks_to_google_calendar()`
Sync all tasks with due dates to Google Calendar as all-day events.

### Email Agent View (`ui/email_agent_view.py`)

#### `render_email_agent()`
Render the Email Agent chat interface.

**Features**:
- Email selector dropdown
- Selected email info display
- Example query buttons
- Chat interface for asking questions about specific emails
- Uses stored prompts for consistent behavior
- Generates draft replies when requested
- Shows extracted tasks and events for context

### Drafts View (`ui/drafts_view.py`)

#### `render_drafts()`
Render the drafts management view with tabs.

#### `render_saved_drafts()`
List and manage saved drafts.

**Features**:
- Display all saved drafts
- Edit drafts
- View metadata and suggested follow-ups

#### `render_new_draft()`
Create new email drafts or replies.

**Features**:
- Generate new email drafts
- Generate replies to existing emails
- Tone selection
- User requirements input
- Automatic suggested follow-ups generation
- Metadata extraction (category, priority, type)

### Tasks View (`ui/tasks_view.py`)

#### `render_tasks()`
Render the tasks Kanban board.

**Displays**:
- Three columns: To Do, In Progress, Done
- Task cards with status dropdowns
- Links to source emails

### Files View (`ui/files_view.py`)

#### `render_files()`
Render the attachments hub.

**Features**:
- List all attachments
- Filter by file type
- Link to source emails
- Summary statistics

### Settings View (`ui/settings_view.py`)

#### `render_settings()`
Render the settings view with tabs.

#### `render_mode_selection()`
Render mode selection interface (Mock vs Gmail).

#### `render_prompt_brain()`
Render prompt customization interface.

### Layout (`ui/layout.py`)

#### `render_sidebar()`
Render the sidebar with navigation, quick stats, and mode indicator.

**Features**:
- Navigation menu (Dashboard, Inbox, Email Agent, Calendar, Tasks, Files, Drafts, Settings)
- Quick stats (unread emails, tasks, events)
- Mode indicator (Mock or Gmail API)

---

## Main Application

**File**: `app.py`

**Purpose**: Entry point and routing.

### Function: `main()`
Main application entry point.

**Flow**:
1. Set Streamlit page config
2. Initialize session state
3. Set default page if not set
4. Render sidebar
5. Route to appropriate view based on `st.session_state.page`

**Views**:
- `dashboard`: Dashboard view
- `inbox`: Inbox view
- `email_agent`: Email Agent chat interface
- `calendar`: Calendar view
- `tasks`: Tasks view
- `files`: Files view
- `drafts`: Drafts management view
- `settings`: Settings view

---

## Summary

This codebase is organized into:

- **Core Layer**: Data models, LLM client, processors, data loaders
- **UI Layer**: Views and components for user interaction
- **State Layer**: Session state management
- **Config Layer**: Configuration and constants

The architecture supports:
- Multiple LLM providers
- Multiple data sources (Mock, Gmail)
- Extensible processing pipeline
- Modular UI components

All modules are well-documented with docstrings and type hints for maintainability.

