# Smart Email Agent 📧

A Streamlit-based Smart Email Agent powered by LLM that helps users understand and organize their inbox. This is a **Prompt-Driven Email Productivity Agent** that processes emails (real or mock) and performs automated tasks such as email categorization, action-item extraction, auto-drafting replies, and chat-based inbox interaction.

The system uses user-defined prompts ("the agent brain") to guide all LLM-powered operations. The app can work with mock inbox data for demos or connect to a real Gmail account via the Gmail API.

## Features

### Core Features
- **Email Categorization**: Automatically categorizes emails (Work, Personal, To-Do, Newsletter, Spam, etc.) and assigns priority levels
- **Task Extraction**: Extracts actionable tasks from emails with due dates
- **Event/Deadline Extraction**: Identifies meetings and deadlines from email content
- **Draft Reply Generation**: Generates draft replies with customizable tone (Formal, Friendly, Concise, etc.)
- **Chat-style Inbox Interaction**: Ask questions about your inbox in natural language

### Productivity Features
- **Today Dashboard**: Overview of unread emails, tasks, and upcoming events
- **Calendar View**: View and manage events extracted from emails
- **Task Board (Kanban)**: Organize tasks in To Do, In Progress, and Done columns
- **Attachments Hub**: Browse and filter email attachments by type
- **Reminders**: Set reminders linked to specific emails
- **Sender Context**: Get AI-generated context about email senders

### Advanced Features
- **Prompt Brain**: Create, edit, and save all LLM prompts to JSON file (persistent storage)
- **Draft Management**: Generate new email drafts or replies, edit them, and save with metadata
- **Suggested Follow-ups**: AI-generated follow-up suggestions for each draft
- **Explanation Mode**: Understand why emails were categorized or processed a certain way
- **Tone & Completeness Check**: Review draft replies for appropriateness and completeness
- **Two Modes**: 
  - **Mock Inbox Mode**: Use sample emails for demos (no authentication needed)
  - **Gmail API Mode**: Connect to real Gmail account (OAuth 2.0)
- **Safety**: All drafts are stored locally, never auto-sent

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Ollama installed and running locally (or use OpenAI with API key)

### Installation

1. **Install Ollama** (if not already installed):
   - Visit [https://ollama.ai](https://ollama.ai) and download Ollama for your OS
   - Install and start Ollama service
   - Pull a model (recommended: `llama2:latest`, `llama3.2`, or `mistral`):
     ```bash
     ollama pull llama2:latest
     # or
     ollama pull llama3.2
     ```
   - Or use any other model: `ollama pull mistral`, `ollama pull qwen2.5`, etc.

2. **Clone or download this repository**

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**:
   Create a `.env` file in the project root (optional, defaults work for Ollama):
   ```
   LLM_PROVIDER=ollama
   LLM_MODEL=llama2:latest
   OLLAMA_BASE_URL=http://localhost:11434
   ```
   
   **Note**: If you want to use OpenAI instead, set:
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4-turbo-preview
   ```

### Running in Mock Inbox Mode

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Load mock inbox**:
   - Navigate to Settings → Mode Selection
   - Select "Mock Inbox"
   - Click "Load Mock Inbox"
   - The app will load sample emails from `data/mock_inbox.json`

3. **Start using the app**:
   - Emails will be automatically categorized and processed
   - Explore the Dashboard, Inbox, Calendar, Tasks, and Files views

### Running in Gmail API Mode

1. **Set up Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials as `credentials.json` and place it in the project root

2. **Start the app**:
   ```bash
   streamlit run app.py
   ```

3. **Connect to Gmail**:
   - Navigate to Settings → Mode Selection
   - Select "Gmail API"
   - Click "Connect to Gmail"
   - Complete OAuth authentication in the browser
   - Emails will be fetched and processed automatically

**Note**: The app uses read-only Gmail access. It never auto-sends emails.

## Project Structure

```
smart_email_agent/
├── app.py                 # Main Streamlit entry point
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── ARCHITECTURE.md       # System architecture documentation
├── core/                 # Core functionality
│   ├── models.py         # Data models (Email, Task, Event, Reminder)
│   ├── llm_client.py     # LLM abstraction layer
│   ├── prompts.py        # Prompt templates
│   ├── processors.py     # Email processing logic
│   ├── gmail_client.py   # Gmail API wrapper
│   ├── mock_data_loader.py  # Mock inbox loader
│   └── state.py          # Session state management
├── ui/                   # UI components
│   ├── layout.py         # Main layout and sidebar
│   ├── components.py     # Reusable UI components
│   ├── dashboard.py      # Dashboard view
│   ├── inbox_view.py     # Inbox and email detail view
│   ├── calendar_view.py  # Calendar and events view
│   ├── tasks_view.py     # Task board (Kanban)
│   ├── files_view.py     # Attachments hub
│   └── settings_view.py  # Settings and Prompt Brain
├── data/                 # Data files
│   └── mock_inbox.json   # Sample emails for mock mode
└── docs/                 # Documentation
    └── APP_DOCUMENTATION.md  # Detailed code documentation
```

## Usage Guide

### Dashboard
The default view shows:
- Statistics (unread emails, tasks, events)
- High priority unread emails
- Upcoming deadlines
- Next meetings
- Top tasks

### Inbox
- View all emails with filtering options
- Click "View" to see email details
- Generate draft replies
- Set reminders
- View sender context

### Calendar
- View events by date
- Manage suggested events from emails
- Confirm, edit, or ignore extracted events

### Tasks
- Kanban board with To Do, In Progress, and Done columns
- Change task status
- View source email for each task

### Files
- Browse all email attachments
- Filter by file type (PDF, DOC, images, etc.)
- View attachment details and source email

### Settings
- **Mode Selection**: Switch between Mock Inbox and Gmail API
- **Prompt Brain**: Customize all LLM prompts used by the system

### Chat with Inbox
Use the sidebar to ask questions like:
- "Summarize my unread emails from today"
- "Show tasks due this week"
- "Find emails about the DBMS project"

## Configuration

### LLM Configuration
Edit `config.py` or set environment variables to customize:
- **LLM Provider**: Default is `ollama` (can be changed to `openai`)
- **LLM Model**: Default is `llama2:latest` (change to any Ollama model you have installed)
- **Ollama Base URL**: Default is `http://localhost:11434`

**Environment Variables** (in `.env` file):
```bash
LLM_PROVIDER=ollama          # or "openai"
LLM_MODEL=llama2:latest      # or "llama3.2", "mistral", "qwen2.5", etc.
OLLAMA_BASE_URL=http://localhost:11434
```

### Prompt Configuration
All prompts are stored in `data/prompts.json` and can be customized via the **Prompt Brain** in Settings:
- **Categorization Prompt**: How emails are categorized
- **Task Extraction Prompt**: How action items are extracted
- **Event Extraction Prompt**: How meetings/deadlines are extracted
- **Reply Generation Prompt**: How replies are generated
- **New Draft Generation Prompt**: How new emails are generated
- **Other Prompts**: Explanation, tone check, sender context, inbox query

Prompts are automatically saved to file when edited in the UI.

## Security Notes

- **Never commit** `credentials.json`, `token.json`, or `.env` files
- The app uses read-only Gmail access (no auto-sending)
- API keys should be stored in environment variables
- OAuth tokens are stored locally in `token.json`

## Troubleshooting

### Ollama Connection Errors
- **"Cannot connect to Ollama"**: Make sure Ollama is running
  - On Windows: Check if Ollama service is running
  - On Mac/Linux: Run `ollama serve` in terminal
  - Verify Ollama is accessible at `http://localhost:11434`
- **"Model not found"**: Pull the model first with `ollama pull <model_name>`
  - Example: `ollama pull llama2:latest` or `ollama pull llama3.2`
- **Slow responses**: Try a smaller/faster model like `llama3.2:1b` or `mistral:7b`

### OpenAI API Errors (if using OpenAI)
- Verify your API key is set correctly in `.env`
- Check your API quota/limits
- Ensure you have internet connectivity

### Gmail Authentication Issues
- Verify `credentials.json` is in the project root
- Check that Gmail API is enabled in Google Cloud Console
- Delete `token.json` and re-authenticate if needed

### Mock Inbox Not Loading
- Check that `data/mock_inbox.json` exists
- The app will generate sample emails if the file is missing

## Assignment Requirements Compliance

This project satisfies all assignment requirements:

### ✅ Phase 1: Email Ingestion & Knowledge Base
- ✅ Load emails (Mock Inbox or Gmail API)
- ✅ View list of emails with sender, subject, timestamp, category tags
- ✅ Create and edit prompt configurations (Prompt Brain panel)
- ✅ Store prompts in JSON file (`data/prompts.json`)
- ✅ Store processed outputs (categories, tasks, events in session state)
- ✅ Ingestion pipeline: Load → Categorize → Extract → Save → Update UI

### ✅ Phase 2: Email Processing Agent
- ✅ "Email Agent" chat interface in sidebar
- ✅ Select email and ask questions ("Summarize this email", "What tasks do I need to do?")
- ✅ Draft replies based on tone
- ✅ General inbox queries ("Show me all urgent emails")
- ✅ Agent uses stored prompts and email content

### ✅ Phase 3: Draft Generation Agent
- ✅ Generate new email drafts (not just replies)
- ✅ Generate replies to existing emails
- ✅ Edit drafts
- ✅ Save drafts with metadata (JSON format)
- ✅ Suggested follow-ups for each draft
- ✅ Uses auto-reply prompt for replies
- ✅ Uses new draft generation prompt for new emails
- ✅ Never auto-sends emails (safety first)

### ✅ Project Assets
- ✅ Mock Inbox: `data/mock_inbox.json` with 15+ sample emails
- ✅ Default Prompt Templates: All prompts in `core/prompts.py`
- ✅ README.md: Complete setup and usage instructions

## Extending the App

### Adding a New LLM Provider
1. Update `core/llm_client.py` to support the new provider
2. Add provider-specific configuration in `config.py`
3. Update `requirements.txt` with provider SDK

### Adding New Categories
1. Update the categorization prompt in `core/prompts.py`
2. Add category icons in `ui/components.py`

### Customizing Prompts
Use the Prompt Brain in Settings to customize all prompts without editing code.

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues or questions, please refer to:
- `ARCHITECTURE.md` for system design details
- `docs/APP_DOCUMENTATION.md` for code documentation

