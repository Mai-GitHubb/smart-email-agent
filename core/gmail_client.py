"""
Gmail API client wrapper.

Handles OAuth authentication and Gmail API operations.
Supports credentials from files (local) or JSON strings (Streamlit Cloud).
"""
import os
import base64
import json
import tempfile
from typing import List, Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config
from core.models import Email


class GmailClient:
    """Wrapper for Gmail API operations."""
    
    def __init__(self, credentials_file: str = None, token_file: str = None):
        """
        Initialize Gmail client.
        
        Args:
            credentials_file: Path to OAuth credentials JSON file
            token_file: Path to store/load OAuth token
        """
        self.credentials_file = credentials_file or config.GMAIL_CREDENTIALS_FILE
        self.token_file = token_file or config.GMAIL_TOKEN_FILE
        self.service = None
        self.creds = None
        self._temp_credentials_file = None  # For credentials from secrets
    
    def _get_credentials_file(self) -> Optional[str]:
        """
        Get credentials file path, creating temp file from secrets if needed.
        
        Returns:
            Path to credentials file, or None if not available
        """
        # First, check if credentials JSON string is available (from Streamlit secrets)
        if config.GMAIL_CREDENTIALS_JSON:
            try:
                # Parse JSON to validate
                creds_data = json.loads(config.GMAIL_CREDENTIALS_JSON)
                # Create temporary file for credentials
                if self._temp_credentials_file is None or not os.path.exists(self._temp_credentials_file):
                    temp_fd, temp_path = tempfile.mkstemp(suffix='.json', prefix='gmail_creds_')
                    with os.fdopen(temp_fd, 'w') as f:
                        json.dump(creds_data, f)
                    self._temp_credentials_file = temp_path
                return self._temp_credentials_file
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error parsing Gmail credentials JSON: {e}")
                # Fall back to file
        
        # Fall back to credentials file
        if os.path.exists(self.credentials_file):
            return self.credentials_file
        
        return None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth 2.0.
        Supports credentials from file or JSON string (Streamlit secrets).
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing token
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, config.GMAIL_SCOPES)
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Get credentials file (from secrets or file)
                    creds_file = self._get_credentials_file()
                    if not creds_file:
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        creds_file, config.GMAIL_SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run (only if token file path is writable)
                try:
                    with open(self.token_file, 'w') as token:
                        token.write(self.creds.to_json())
                except Exception as e:
                    # In Streamlit Cloud, token file might not be writable
                    # This is okay, credentials will be refreshed on next run
                    print(f"Note: Could not save token file: {e}")
            
            # Build service
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Gmail authentication error: {e}")
            return False
    
    def fetch_emails(self, max_results: int = 50, query: str = None) -> List[Email]:
        """
        Fetch emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query (e.g., "is:unread")
            
        Returns:
            List of Email objects
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Build query
            if query is None:
                query = ""
            
            # List messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=min(max_results, config.MAX_EMAILS_TO_FETCH),
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                try:
                    email = self._fetch_email_details(msg['id'])
                    if email:
                        emails.append(email)
                except Exception as e:
                    print(f"Error fetching email {msg['id']}: {e}")
                    continue
            
            return emails
        except HttpError as e:
            print(f"Gmail API error: {e}")
            return []
    
    def _fetch_email_details(self, message_id: str) -> Optional[Email]:
        """
        Fetch detailed information for a single email.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Email object or None
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            headers_dict = {h['name']: h['value'] for h in headers}
            
            sender = headers_dict.get('From', '')
            sender_name = sender.split('<')[0].strip().strip('"')
            sender_email = sender.split('<')[-1].strip('>') if '<' in sender else sender
            
            subject = headers_dict.get('Subject', 'No Subject')
            date_str = headers_dict.get('Date', '')
            
            # Parse date
            try:
                from email.utils import parsedate_to_datetime
                timestamp = parsedate_to_datetime(date_str)
            except:
                timestamp = datetime.now()
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Extract labels
            labels = message.get('labelIds', [])
            
            # Check for attachments
            has_attachments = False
            attachments = []
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('filename'):
                        has_attachments = True
                        attachments.append({
                            'name': part['filename'],
                            'type': part.get('mimeType', 'unknown'),
                            'size': part.get('body', {}).get('size', 0)
                        })
            
            return Email(
                id=message_id,
                sender=sender_email,
                sender_name=sender_name,
                subject=subject,
                body=body,
                timestamp=timestamp,
                labels=labels,
                has_attachments=has_attachments,
                attachments=attachments,
                is_read='UNREAD' not in labels,
                thread_id=message.get('threadId')
            )
        except Exception as e:
            print(f"Error parsing email {message_id}: {e}")
            return None
    
    def _extract_body(self, payload: dict) -> str:
        """
        Extract email body from Gmail payload.
        Handles nested multipart messages and prefers plain text over HTML.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            Email body text
        """
        body_text = ""
        body_html = ""
        
        def extract_from_part(part: dict):
            """Recursively extract body from a part."""
            nonlocal body_text, body_html
            
            mime_type = part.get('mimeType', '')
            
            # If this part has nested parts, recurse
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_from_part(subpart)
            else:
                # Extract body data
                body_data = part.get('body', {}).get('data')
                if body_data:
                    try:
                        decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        if mime_type == 'text/plain' and not body_text:
                            body_text = decoded
                        elif mime_type == 'text/html' and not body_html:
                            body_html = decoded
                    except Exception as e:
                        print(f"Error decoding body part: {e}")
        
        # Check if payload has parts (multipart message)
        if 'parts' in payload:
            for part in payload['parts']:
                extract_from_part(part)
        else:
            # Single part message
            mime_type = payload.get('mimeType', '')
            body_data = payload.get('body', {}).get('data')
            if body_data:
                try:
                    decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                    if mime_type == 'text/plain':
                        body_text = decoded
                    elif mime_type == 'text/html':
                        body_html = decoded
                except Exception as e:
                    print(f"Error decoding body: {e}")
        
        # Prefer plain text, fall back to HTML (strip HTML tags)
        if body_text:
            return body_text.strip()
        elif body_html:
            # Simple HTML tag removal (basic approach)
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', body_html)
            # Decode common HTML entities
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            text = text.replace('&#39;', "'")
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Remove extra newlines
            text = re.sub(r'\n\s*\n', '\n\n', text)
            return text
        
        return ""
    
    def is_authenticated(self) -> bool:
        """
        Check if client is authenticated.
        
        Returns:
            True if authenticated
        """
        return self.service is not None

