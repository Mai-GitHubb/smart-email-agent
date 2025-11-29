# Smart Email Agent - Architecture Documentation

## System Overview

The Smart Email Agent is a Streamlit-based application that uses LLM (Large Language Model) to process, categorize, and extract information from emails. The system is designed with modularity and extensibility in mind.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                      │
│  (Dashboard, Inbox, Calendar, Tasks, Files, Settings)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Session State Layer                      │
│         (Email storage, Tasks, Events, Reminders)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                         │
│  (EmailProcessor: Categorization, Extraction, Generation)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM Client Layer                       │
│              (Abstraction for LLM providers)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Source Layer                        │
│         (Mock Data Loader | Gmail API Client)              │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Core Modules (`core/`)

#### `models.py`
**Purpose**: Defines data structures used throughout the application.

**Key Classes**:
- `Email`: Represents an email message with metadata
- `Task`: Represents an extracted task with due date and status
- `Event`: Represents a meeting or deadline extracted from emails
- `Reminder`: Represents a reminder linked to an email
- `CategoryResult`: Result of email categorization

**Data Flow**: Models are used to pass data between layers.

#### `llm_client.py`
**Purpose**: Provides abstraction layer for LLM API calls.

**Key Functions**:
- `categorize_email()`: Categorizes an email and assigns priority
- `extract_tasks()`: Extracts actionable tasks from email
- `extract_events()`: Extracts meetings/deadlines from email
- `generate_reply()`: Generates draft reply text
- `explain_decision()`: Explains categorization/extraction decisions
- `check_reply_tone()`: Validates reply tone and completeness
- `get_sender_context()`: Generates context about a sender
- `process_inbox_query()`: Processes natural language queries

**Design Pattern**: Strategy pattern - can swap LLM providers without changing calling code.

#### `prompts.py`
**Purpose**: Centralized storage of all prompt templates.

**Prompts**:
- `CATEGORIZATION_PROMPT`: For email categorization
- `TASK_EXTRACTION_PROMPT`: For task extraction
- `EVENT_EXTRACTION_PROMPT`: For event/deadline extraction
- `REPLY_GENERATION_PROMPT`: For reply generation
- `EXPLANATION_PROMPT`: For explaining decisions
- `REPLY_TONE_CHECK_PROMPT`: For tone validation
- `SENDER_CONTEXT_PROMPT`: For sender context
- `INBOX_QUERY_PROMPT`: For natural language queries

**Design**: Prompts are stored as template strings with placeholders.

#### `processors.py`
**Purpose**: Orchestrates email processing using LLM client.

**Key Class**: `EmailProcessor`

**Methods**:
- `categorize_email()`: Wrapper for LLM categorization
- `extract_tasks()`: Wrapper for task extraction
- `extract_events()`: Wrapper for event extraction
- `process_email()`: Comprehensive processing (all operations)
- `batch_process_emails()`: Process multiple emails

**Design**: Facade pattern - simplifies LLM client usage.

#### `gmail_client.py`
**Purpose**: Wraps Gmail API for fetching emails.

**Key Class**: `GmailClient`

**Methods**:
- `authenticate()`: OAuth 2.0 authentication
- `fetch_emails()`: Fetch emails from Gmail (up to 100 emails)
- `_fetch_email_details()`: Get detailed email information
- `_extract_body()`: Extract email body from Gmail payload (handles nested multipart, HTML conversion)

**Security**: Uses OAuth 2.0, read-only access, tokens stored locally.

#### `google_calendar_client.py`
**Purpose**: Wraps Google Calendar API for syncing tasks and events.

**Key Class**: `GoogleCalendarClient`

**Methods**:
- `authenticate()`: OAuth 2.0 authentication with Calendar scopes
- `add_task_as_event()`: Add a task as an all-day event to Google Calendar
- `add_event()`: Add an event to Google Calendar with time and location

**Integration**: Allows users to sync extracted tasks and confirmed events to their Google Calendar.

#### `date_utils.py`
**Purpose**: Date parsing utilities for handling various date formats.

**Key Functions**:
- `parse_date()`: Parse date strings in multiple formats (ISO, "Fri, 28 Nov, 2025", etc.)
- `normalize_date()`: Normalize date string to YYYY-MM-DD format

**Features**: Handles various date formats returned by LLMs, with fallback to dateutil if available.

#### `prompt_storage.py`
**Purpose**: Handles saving and loading prompts to/from JSON file.

**Key Functions**:
- `load_prompts()`: Load prompts from `data/prompts.json` or return defaults
- `save_prompts()`: Save prompts to `data/prompts.json`
- `get_default_prompts()`: Get default prompt templates

**Persistence**: Ensures user-edited prompts persist across application sessions.

#### `mock_data_loader.py`
**Purpose**: Loads sample emails for demo/testing.

**Key Function**: `load_mock_inbox()`

**Features**:
- Loads from JSON file
- Falls back to generated sample data if file missing
- Returns list of `Email` objects

#### `state.py`
**Purpose**: Manages Streamlit session state.

**Key Functions**:
- `initialize_state()`: Sets up all state variables
- `get_email()`: Retrieve email by ID
- `add_task()`, `add_event()`, `add_reminder()`: Add items to state
- Filter functions: `get_tasks_by_status()`, `get_events_by_date()`, etc.
- Update functions: `update_task_status()`, `confirm_event()`, etc.

**Design**: Centralized state management to avoid scattered state access.

### UI Modules (`ui/`)

#### `layout.py`
**Purpose**: Main layout and navigation.

**Key Function**: `render_sidebar()`
- Navigation menu
- Chat with inbox interface
- Quick stats display
- Mode indicator

#### `components.py`
**Purpose**: Reusable UI components.

**Components**:
- `priority_badge()`: Returns emoji for priority
- `category_icon()`: Returns emoji for category
- `email_card()`: Displays email as card
- `task_card()`: Displays task as card
- `event_card()`: Displays event as card
- `info_card()`, `stat_card()`: Display cards

#### `dashboard.py`
**Purpose**: Today's overview dashboard.

**Key Function**: `render_dashboard()`
- Statistics row
- High priority emails
- Upcoming deadlines
- Next meetings
- Top tasks
- Quick actions

#### `inbox_view.py`
**Purpose**: Email list and detail view.

**Key Functions**:
- `render_inbox()`: Email list with filters
- `render_email_detail()`: Detailed email view
- `render_reply_tab()`: Reply generation
- `render_explain_tab()`: Explanation generation
- `render_reminder_tab()`: Reminder setting
- `render_sender_context_tab()`: Sender context

#### `calendar_view.py`
**Purpose**: Calendar and events management.

**Key Functions**:
- `render_calendar()`: Main calendar view
- `render_calendar_view()`: Month view with date selector
- `render_suggested_events()`: Manage suggested events

#### `tasks_view.py`
**Purpose**: Kanban task board.

**Key Function**: `render_tasks()`
- Three columns: To Do, In Progress, Done
- Status change dropdowns
- Link to source emails

#### `files_view.py`
**Purpose**: Attachments hub.

**Key Function**: `render_files()`
- List all attachments
- Filter by file type
- Link to source emails
- Summary statistics

#### `settings_view.py`
**Purpose**: Settings and configuration.

**Key Functions**:
- `render_settings()`: Main settings view with tabs
- `render_mode_selection()`: Switch between Mock/Gmail modes
- `render_prompt_brain()`: Customize LLM prompts (all prompts editable and savable)

#### `email_agent_view.py`
**Purpose**: Dedicated Email Agent chat interface.

**Key Function**: `render_email_agent()`

**Features**:
- Email selector dropdown
- Selected email info display
- Example query buttons
- Chat interface for asking questions about specific emails
- Uses stored prompts for consistent behavior
- Generates draft replies when requested

#### `drafts_view.py`
**Purpose**: Draft management (new emails and replies).

**Key Functions**:
- `render_drafts()`: Main drafts view with tabs
- `render_saved_drafts()`: List and manage saved drafts
- `render_new_draft()`: Create new drafts or replies

**Features**:
- Generate new email drafts
- Generate replies to existing emails
- Edit and save drafts
- Metadata and suggested follow-ups for each draft

### Main Application (`app.py`)

**Purpose**: Entry point and routing.

**Flow**:
1. Initialize Streamlit page config
2. Initialize session state
3. Render sidebar (navigation)
4. Route to appropriate view based on `st.session_state.page`

## Data Flow

### Email Processing Flow

```
1. User loads emails (Mock or Gmail)
   ↓
2. Emails stored in st.session_state.emails
   ↓
3. EmailProcessor.process_email() called for each email
   ↓
4. LLMClient methods called with prompts
   ↓
5. Results stored:
   - Email.category, Email.priority
   - Tasks added to st.session_state.tasks
   - Events added to st.session_state.events
   ↓
6. UI displays processed data
```

### Reply Generation Flow

```
1. User selects email and clicks "Generate Reply"
   ↓
2. User selects tone and optional instructions
   ↓
3. LLMClient.generate_reply() called
   ↓
4. Draft displayed in text area
   ↓
5. Optional: User clicks "Check Tone & Completeness"
   ↓
6. LLMClient.check_reply_tone() called
   ↓
7. Feedback displayed
```

### Task/Event Extraction Flow

```
1. Email processed by EmailProcessor
   ↓
2. LLMClient.extract_tasks() or extract_events() called
   ↓
3. JSON response parsed into Task/Event objects
   ↓
4. Objects added to session state
   ↓
5. UI displays in Tasks/Calendar views
```

## Design Patterns

### 1. Strategy Pattern
- **LLM Client**: Can swap providers (OpenAI, Anthropic, etc.) without changing calling code
- **Data Source**: Mock vs Gmail modes use same interface

### 2. Facade Pattern
- **EmailProcessor**: Simplifies LLM client usage
- **State Functions**: Provide simple interface to complex state management

### 3. Template Method Pattern
- **Prompts**: Template strings with placeholders filled at runtime

### 4. Observer Pattern (implicit)
- **Streamlit**: UI updates automatically when state changes

## Extension Points

### Adding New LLM Provider
1. Update `LLMClient.__init__()` to handle new provider
2. Implement provider-specific `_call_llm()` logic
3. Add configuration in `config.py`

### Adding New Email Source
1. Create new client class (similar to `GmailClient`)
2. Implement `fetch_emails()` method returning `List[Email]`
3. Add mode option in `settings_view.py`

### Adding New Processing Feature
1. Add prompt template in `prompts.py`
2. Add method in `LLMClient`
3. Add wrapper in `EmailProcessor`
4. Add UI in appropriate view

### Adding New Category
1. Update categorization prompt
2. Add icon in `ui/components.py`
3. Update filter options in `inbox_view.py`

## Error Handling

- **LLM API Errors**: Caught and logged, fallback to defaults
- **Gmail API Errors**: Caught and displayed to user
- **File Errors**: Mock loader generates sample data if file missing
- **State Errors**: Functions return None/empty lists on errors

## Performance Considerations

- **Batch Processing**: `batch_process_emails()` for multiple emails
- **Caching**: Processing results cached in `st.session_state.processing_cache`
- **Lazy Loading**: Emails processed on-demand or in batches
- **Pagination**: Gmail API supports pagination (not fully implemented)

## Security Considerations

- **API Keys**: Stored in environment variables, never committed
- **OAuth Tokens**: Stored locally in `token.json`, not committed
- **Read-Only Access**: Gmail API uses read-only scope
- **No Auto-Send**: Reply generation only, no sending capability

## Future Enhancements

1. **Database Storage**: Replace in-memory state with SQLite/PostgreSQL
2. **Multi-Provider Support**: Add Anthropic, Cohere, etc.
3. **Email Sending**: Optional send capability (with confirmation)
4. **Search**: Full-text search across emails
5. **Analytics**: Email statistics and trends
6. **Multi-Account**: Support multiple Gmail accounts
7. **Offline Mode**: Cache LLM responses for offline use
8. **Email Threading**: Better thread view and management
9. **Advanced Filtering**: More sophisticated email filtering options
10. **Export Functionality**: Export drafts, tasks, events to various formats

