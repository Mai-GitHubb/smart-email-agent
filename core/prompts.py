"""
Prompt templates for LLM interactions.

All prompts used by the Smart Email Agent are defined here.
These can be customized via the Prompt Brain panel in the UI.
"""

# Email Categorization Prompt
CATEGORIZATION_PROMPT = """You are an email categorization assistant. Analyze the following email and categorize it.

Email:
From: {sender}
Subject: {subject}
Body: {body}

Please categorize this email and assign a priority level.

Respond in JSON format:
{{
    "category": "Work" | "Personal" | "To-Do" | "Newsletter" | "Spam" | "Meeting" | "Deadline" | "Other",
    "priority": "High" | "Medium" | "Low",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Only return the JSON, no additional text."""

# Action Item Extraction Prompt
TASK_EXTRACTION_PROMPT = """You are a task extraction assistant. Analyze the following email and extract any action items or tasks.

Email:
From: {sender}
Subject: {subject}
Body: {body}

Extract all actionable tasks mentioned in this email. For each task, identify:
- A clear title/description
- Due date if mentioned (format: YYYY-MM-DD)
- Any relevant notes or context

Respond in JSON format as an array:
[
    {{
        "task_id": "unique_id",
        "title": "task description",
        "due_date": "YYYY-MM-DD or null",
        "source_email_id": "{email_id}",
        "status": "todo",
        "notes": "any contextual information"
    }}
]

If no tasks are found, return an empty array [].

Only return the JSON array, no additional text."""

# Event/Deadline Extraction Prompt
EVENT_EXTRACTION_PROMPT = """You are an event and deadline extraction assistant. Analyze the following email and extract any meetings, events, or deadlines.

Email:
From: {sender}
Subject: {subject}
Body: {body}

Extract all events, meetings, or deadlines mentioned. For each, identify:
- Type: "meeting" or "deadline"
- Title/description
- Date (format: YYYY-MM-DD)
- Start time if mentioned (format: HH:MM)
- End time if mentioned (format: HH:MM)
- Location if mentioned
- Participants if mentioned

Respond in JSON format as an array:
[
    {{
        "event_id": "unique_id",
        "type": "meeting" | "deadline",
        "title": "event title",
        "date": "YYYY-MM-DD",
        "start_time": "HH:MM or null",
        "end_time": "HH:MM or null",
        "all_day": true/false,
        "location": "string or null",
        "participants": ["email or name"],
        "source_email_id": "{email_id}",
        "confidence": 0.0-1.0
    }}
]

If no events are found, return an empty array [].

Only return the JSON array, no additional text."""

# Reply Generation Prompt
REPLY_GENERATION_PROMPT = """You are an email reply assistant. Generate a draft reply to the following email.

Original Email:
From: {sender}
Subject: {subject}
Body: {body}

User Instructions: {user_instructions}

Tone: {tone}

Generate a professional draft reply that:
- Addresses all points in the original email
- Matches the requested tone ({tone})
- Is appropriate and polite
- Is concise but complete

Return only the reply text, no additional formatting or explanations."""

# New Draft Email Generation Prompt
NEW_DRAFT_GENERATION_PROMPT = """You are an email composition assistant. Generate a new email draft based on the user's requirements.

User Requirements:
{user_requirements}

Recipient: {recipient}
Tone: {tone}
Subject: {subject}

Generate a professional email draft that:
- Matches the requested tone ({tone})
- Is appropriate and polite
- Is clear and well-structured
- Includes all necessary information

Return only the email body text, no additional formatting or explanations."""

# Explanation Prompt
EXPLANATION_PROMPT = """Explain why this email was categorized and processed the way it was.

Email:
From: {sender}
Subject: {subject}
Body: {body}

Category: {category}
Priority: {priority}
Extracted Tasks: {tasks}
Extracted Events: {events}

Provide a clear, concise explanation of:
1. Why this category was assigned
2. Why this priority level was chosen
3. What tasks/events were identified and why

Keep the explanation brief and easy to understand."""

# Reply Tone Check Prompt
REPLY_TONE_CHECK_PROMPT = """Review the following email reply draft for tone and completeness.

Original Email:
From: {sender}
Subject: {subject}
Body: {original_body}

Draft Reply:
{draft_reply}

Requested Tone: {requested_tone}

Evaluate:
1. Is the tone appropriate and matches the requested tone?
2. Is it polite and professional?
3. Are all questions in the original email answered?
4. Are there any issues or improvements needed?

Respond in JSON format:
{{
    "tone_appropriate": true/false,
    "is_polite": true/false,
    "all_questions_answered": true/false,
    "feedback": "detailed feedback",
    "suggestions": ["suggestion1", "suggestion2"]
}}

Only return the JSON, no additional text."""

# Sender Context Prompt
SENDER_CONTEXT_PROMPT = """Analyze the email history with this sender and provide context.

Sender: {sender_name} ({sender_email})

Recent Emails:
{recent_emails}

Provide a brief summary (2-3 sentences) about:
- The nature of emails from this sender
- Common topics or themes
- The relationship context (work, personal, etc.)

Keep it concise and informative."""

# Inbox Query Prompt
INBOX_QUERY_PROMPT = """You are an inbox assistant. The user has asked: "{query}"

Available Information:
- Total emails: {total_emails}
- Unread emails: {unread_count}
- Categories: {categories}
- Tasks: {tasks_summary}
- Events: {events_summary}

Based on this query, determine what information the user needs and provide a helpful response.
If the query asks for specific emails, tasks, or events, list them clearly.
If it asks for a summary, provide a concise summary.

Respond in a natural, conversational way."""

