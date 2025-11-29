"""
Configuration file for Smart Email Agent.

Contains constants, configuration flags, and environment variable handling.
All configuration can be overridden via environment variables in a .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
# This allows users to configure the app without modifying code
load_dotenv()

# ============================================================================
# LLM Configuration
# ============================================================================
# The application uses an LLM abstraction layer that supports multiple providers
# Default is Ollama (local, free), but can be switched to OpenAI or others

# LLM Provider: "ollama" (default, local) or "openai" (cloud, requires API key)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# LLM Model: For Ollama, use models like "llama2:latest", "llama3.2", "mistral", "qwen2.5"
# For OpenAI, use models like "gpt-4-turbo-preview", "gpt-3.5-turbo"
LLM_MODEL = os.getenv("LLM_MODEL", "llama2:latest")

# Ollama Base URL: Where the Ollama server is running (default: localhost)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# OpenAI Configuration (optional, only needed if using OpenAI provider)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# ============================================================================
# Gmail API Configuration
# ============================================================================
# Required for Gmail API mode (OAuth 2.0 authentication)
# Get credentials from Google Cloud Console

GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
# Read-only scope - the app never sends emails, only reads
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ============================================================================
# Google Calendar API Configuration
# ============================================================================
# Required for syncing tasks and events to Google Calendar
# Uses same credentials file as Gmail by default, but can be separate

GOOGLE_CALENDAR_CREDENTIALS_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", GMAIL_CREDENTIALS_FILE)
GOOGLE_CALENDAR_TOKEN_FILE = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "calendar_token.json")
# Calendar events scope - allows creating events in user's calendar
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# ============================================================================
# Application Configuration
# ============================================================================
APP_TITLE = "Smart Email Agent"
APP_ICON = "📧"
# Default mode: "mock" for mock inbox (no authentication), "gmail" for Gmail API
DEFAULT_MODE = "mock"

# ============================================================================
# Data Storage Configuration
# ============================================================================
DATA_DIR = "data"  # Directory for storing data files
MOCK_INBOX_FILE = os.path.join(DATA_DIR, "mock_inbox.json")  # Mock email data file

# ============================================================================
# UI Configuration
# ============================================================================
ITEMS_PER_PAGE = 20  # Number of items per page in paginated views
MAX_EMAILS_TO_FETCH = 100  # Maximum number of emails to fetch from Gmail API

# ============================================================================
# Processing Configuration
# ============================================================================
ENABLE_AUTO_CATEGORIZATION = True  # Automatically categorize emails on load
ENABLE_AUTO_EXTRACTION = True  # Automatically extract tasks/events on load
DEFAULT_PRIORITY = "Medium"  # Default priority for emails if not determined

