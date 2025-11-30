"""
Configuration file for Smart Email Agent.

Contains constants, configuration flags, and environment variable handling.
Configuration priority:
1. Streamlit secrets (st.secrets) - for Streamlit Cloud deployment
2. Environment variables (.env file) - for local development
3. Default values

All configuration can be overridden via environment variables in a .env file
or via Streamlit secrets for cloud deployment.
"""
import os
from dotenv import load_dotenv

# Try to import streamlit for secrets (only available when running in Streamlit)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Load environment variables from .env file (if present)
# This allows users to configure the app without modifying code
load_dotenv()


def _get_config(key: str, default: str = "") -> str:
    """
    Get configuration value with priority: Streamlit secrets > Environment variables > Default.
    
    Args:
        key: Configuration key name
        default: Default value if not found
        
    Returns:
        Configuration value as string
    """
    # First, try Streamlit secrets (for cloud deployment)
    if STREAMLIT_AVAILABLE and st is not None:
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                return str(st.secrets[key])
        except Exception:
            pass  # Fall back to env vars if secrets not available
    
    # Fall back to environment variables
    return os.getenv(key, default)

# ============================================================================
# LLM Configuration
# ============================================================================
# The application uses an LLM abstraction layer that supports multiple providers
# Default is Ollama (local, free), but can be switched to OpenAI or others

# LLM Provider: "ollama" (default, local) or "openai" (cloud, requires API key)
LLM_PROVIDER = _get_config("LLM_PROVIDER", "gemini")

# LLM Model: For Ollama, use models like "llama2:latest", "llama3.2", "mistral", "qwen2.5"
# For OpenAI, use models like "gpt-4-turbo-preview", "gpt-3.5-turbo"
LLM_MODEL = _get_config("LLM_MODEL", "gemini-2.5-flash")

# Ollama Base URL: Where the Ollama server is running (default: localhost)
OLLAMA_BASE_URL = _get_config("OLLAMA_BASE_URL", "http://localhost:11434")

# OpenAI Configuration (optional, only needed if using OpenAI provider)
OPENAI_API_KEY = _get_config("OPENAI_API_KEY", "")
OPENAI_MODEL = _get_config("OPENAI_MODEL", "gpt-4-turbo-preview")

# Gemini / Google Generative AI Configuration (optional, only needed if using Gemini provider)
GEMINI_API_KEY = _get_config("GEMINI_API_KEY", "")
GEMINI_MODEL = _get_config("GEMINI_MODEL", "gemini-2.5-flash")

# ============================================================================
# Gmail API Configuration
# ============================================================================
# Required for Gmail API mode (OAuth 2.0 authentication)
# Get credentials from Google Cloud Console
# For Streamlit Cloud, provide GMAIL_CREDENTIALS_JSON in secrets instead of file

GMAIL_CREDENTIALS_FILE = _get_config("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = _get_config("GMAIL_TOKEN_FILE", "token.json")
# Read-only scope - the app never sends emails, only reads
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Gmail credentials as JSON string (for Streamlit Cloud deployment)
# If provided, will be used instead of credentials file
GMAIL_CREDENTIALS_JSON = _get_config("GMAIL_CREDENTIALS_JSON", "")

# ============================================================================
# Google Calendar API Configuration
# ============================================================================
# Required for syncing tasks and events to Google Calendar
# Uses same credentials file as Gmail by default, but can be separate
# For Streamlit Cloud, provide GOOGLE_CALENDAR_CREDENTIALS_JSON in secrets instead of file

GOOGLE_CALENDAR_CREDENTIALS_FILE = _get_config("GOOGLE_CALENDAR_CREDENTIALS_FILE", GMAIL_CREDENTIALS_FILE)
GOOGLE_CALENDAR_TOKEN_FILE = _get_config("GOOGLE_CALENDAR_TOKEN_FILE", "calendar_token.json")
# Calendar events scope - allows creating events in user's calendar
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Google Calendar credentials as JSON string (for Streamlit Cloud deployment)
# If provided, will be used instead of credentials file
# If empty and GMAIL_CREDENTIALS_JSON is provided, will use Gmail credentials
GOOGLE_CALENDAR_CREDENTIALS_JSON = _get_config("GOOGLE_CALENDAR_CREDENTIALS_JSON", "")

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

