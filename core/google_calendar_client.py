"""
Google Calendar API client wrapper.

Handles OAuth authentication and Calendar API operations.
"""
import os
from typing import Optional
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config
from core.models import Task, Event


class GoogleCalendarClient:
    """Wrapper for Google Calendar API operations."""

    def __init__(
        self,
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None,
        scopes: Optional[list] = None,
    ):
        """
        Initialize Calendar client.

        Args:
            credentials_file: Path to OAuth credentials JSON file
            token_file: Path to store/load OAuth token
            scopes: OAuth scopes list
        """
        self.credentials_file = credentials_file or config.GOOGLE_CALENDAR_CREDENTIALS_FILE
        self.token_file = token_file or config.GOOGLE_CALENDAR_TOKEN_FILE
        self.scopes = scopes or config.GOOGLE_CALENDAR_SCOPES
        self.creds: Optional[Credentials] = None
        self.service = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API using OAuth 2.0.

        Returns:
            True if authentication successful, False otherwise.
        """
        try:
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes
                    )
                    self.creds = flow.run_local_server(port=0)

                with open(self.token_file, "w", encoding="utf-8") as token:
                    token.write(self.creds.to_json())

            self.service = build("calendar", "v3", credentials=self.creds)
            return True
        except Exception as e:
            print(f"Google Calendar authentication error: {e}")
            return False

    def add_task_as_event(self, task: Task, calendar_id: str = "primary") -> Optional[str]:
        """
        Add a Task as an all-day event on its due date.

        Args:
            task: Task to add
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            Created event ID, or None on failure.
        """
        if not task.due_date:
            return None

        if not self.service and not self.authenticate():
            return None

        event_body = {
            "summary": task.title,
            "description": (task.notes or "") + f"\n\nSource: Smart Email Agent (Task ID: {task.task_id})",
            "start": {"date": task.due_date},
            "end": {"date": task.due_date},
        }

        try:
            event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )
            return event.get("id")
        except HttpError as e:
            print(f"Google Calendar API error (task event): {e}")
            return None

    def add_event(self, event: Event, calendar_id: str = "primary") -> Optional[str]:
        """
        Add an internal Event to Google Calendar.

        Args:
            event: Event to add
            calendar_id: Calendar ID

        Returns:
            Created event ID, or None.
        """
        if not self.service and not self.authenticate():
            return None

        start: dict
        end: dict

        if event.start_time:
            # Timed event
            start_dt = f"{event.date}T{event.start_time}:00"
            if event.end_time:
                end_dt = f"{event.date}T{event.end_time}:00"
            else:
                # Default to 1 hour duration
                try:
                    dt = datetime.fromisoformat(start_dt)
                    dt_end = dt.replace(hour=min(dt.hour + 1, 23))
                    end_dt = dt_end.isoformat()
                except Exception:
                    end_dt = start_dt

            start = {"dateTime": start_dt}
            end = {"dateTime": end_dt}
        else:
            # All-day event
            start = {"date": event.date}
            end = {"date": event.date}

        event_body = {
            "summary": event.title,
            "description": f"Type: {event.type}\n\nSource: Smart Email Agent (Email ID: {event.source_email_id})",
            "start": start,
            "end": end,
        }

        if event.location:
            event_body["location"] = event.location

        if event.participants:
            event_body["attendees"] = [{"email": p} for p in event.participants]

        try:
            created = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )
            return created.get("id")
        except HttpError as e:
            print(f"Google Calendar API error (event): {e}")
            return None


