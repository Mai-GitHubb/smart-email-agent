"""
Configuration file for Smart Email Agent.

Contains constants, configuration flags, and environment variable handling.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # Options: "ollama", "openai", etc.
LLM_MODEL = os.getenv("LLM_MODEL", "llama2:latest")  # Default Ollama model (llama2:latest, llama3.2, mistral, etc.)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Ollama server URL

# OpenAI Configuration (for fallback or alternative)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# App Configuration
APP_TITLE = "Smart Email Agent"
APP_ICON = "📧"
DEFAULT_MODE = "mock"  # "mock" or "gmail"

# Data Storage
DATA_DIR = "data"
MOCK_INBOX_FILE = os.path.join(DATA_DIR, "mock_inbox.json")

# UI Configuration
ITEMS_PER_PAGE = 20
MAX_EMAILS_TO_FETCH = 100

# Processing Configuration
ENABLE_AUTO_CATEGORIZATION = True
ENABLE_AUTO_EXTRACTION = True
DEFAULT_PRIORITY = "Medium"

