"""
Mock data loader for demo/testing purposes.

Loads sample emails from JSON file for Mock Inbox mode.
"""
import json
import os
from datetime import datetime, timedelta
from typing import List
from core.models import Email
import config


def load_mock_inbox(file_path: str = None) -> List[Email]:
    """
    Load mock emails from a JSON file.
    
    Args:
        file_path: Path to the JSON file (defaults to config.MOCK_INBOX_FILE)
        
    Returns:
        List of Email objects
    """
    if file_path is None:
        file_path = config.MOCK_INBOX_FILE
    
    # If file doesn't exist, generate sample data
    if not os.path.exists(file_path):
        return _generate_sample_emails()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        emails = []
        for item in data:
            # Parse timestamp
            if isinstance(item.get('timestamp'), str):
                timestamp = datetime.fromisoformat(item['timestamp'])
            else:
                timestamp = datetime.now() - timedelta(days=len(emails))
            
            email = Email(
                id=item.get('id', f"mock_{len(emails)}"),
                sender=item.get('sender', 'unknown@example.com'),
                sender_name=item.get('sender_name', 'Unknown Sender'),
                subject=item.get('subject', 'No Subject'),
                body=item.get('body', ''),
                timestamp=timestamp,
                labels=item.get('labels', []),
                has_attachments=item.get('has_attachments', False),
                attachments=item.get('attachments', []),
                is_read=item.get('is_read', False),
                thread_id=item.get('thread_id')
            )
            emails.append(email)
        
        return emails
    except Exception as e:
        print(f"Error loading mock inbox: {e}")
        return _generate_sample_emails()


def _generate_sample_emails() -> List[Email]:
    """
    Generate sample emails for demo purposes.
    
    Returns:
        List of sample Email objects
    """
    base_time = datetime.now()
    sample_emails = [
        {
            "id": "mock_1",
            "sender": "professor.smith@university.edu",
            "sender_name": "Dr. Sarah Smith",
            "subject": "DBMS Mini-Project Deadline Reminder",
            "body": "Dear Students,\n\nThis is a reminder that your DBMS mini-project is due on March 15, 2024. Please submit your project report and code repository link by 11:59 PM.\n\nIf you have any questions, please reach out to me or the TA.\n\nBest regards,\nDr. Smith",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "labels": ["Important", "Work"],
            "has_attachments": True,
            "attachments": [{"name": "project_guidelines.pdf", "type": "application/pdf"}],
            "is_read": False
        },
        {
            "id": "mock_2",
            "sender": "team.lead@company.com",
            "sender_name": "John Martinez",
            "subject": "Team Meeting Tomorrow at 2 PM",
            "body": "Hi team,\n\nWe have a team meeting scheduled for tomorrow (March 10) at 2:00 PM in Conference Room B. Agenda:\n- Q1 Review\n- Project updates\n- Resource allocation\n\nPlease confirm your attendance.\n\nThanks,\nJohn",
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
            "labels": ["Meeting"],
            "has_attachments": False,
            "is_read": False
        },
        {
            "id": "mock_3",
            "sender": "newsletter@techweekly.com",
            "sender_name": "Tech Weekly",
            "subject": "This Week in Tech: AI Breakthroughs",
            "body": "Check out the latest AI developments this week...",
            "timestamp": (base_time - timedelta(hours=12)).isoformat(),
            "labels": ["Newsletter"],
            "has_attachments": False,
            "is_read": True
        },
        {
            "id": "mock_4",
            "sender": "mom@family.com",
            "sender_name": "Mom",
            "subject": "Family Dinner This Weekend",
            "body": "Hi sweetie,\n\nDon't forget about family dinner this Saturday at 6 PM. Your dad is making his famous lasagna!\n\nLove,\nMom",
            "timestamp": (base_time - timedelta(days=3)).isoformat(),
            "labels": ["Personal"],
            "has_attachments": False,
            "is_read": True
        },
        {
            "id": "mock_5",
            "sender": "ta.jones@university.edu",
            "sender_name": "TA Michael Jones",
            "subject": "Assignment 3 Grading Complete",
            "body": "Hello,\n\nAssignment 3 has been graded. Grades are available on the course portal. Average score: 85/100.\n\nIf you have questions about your grade, please schedule office hours.\n\nBest,\nMichael",
            "timestamp": (base_time - timedelta(days=5)).isoformat(),
            "labels": ["Work"],
            "has_attachments": False,
            "is_read": True
        },
        {
            "id": "mock_6",
            "sender": "client@business.com",
            "sender_name": "Robert Chen",
            "subject": "Urgent: Project Proposal Needed",
            "body": "Hi,\n\nWe need the project proposal by end of day today. This is urgent. Please send it as soon as possible.\n\nThanks,\nRobert",
            "timestamp": (base_time - timedelta(hours=3)).isoformat(),
            "labels": ["Urgent", "Work"],
            "has_attachments": False,
            "is_read": False
        },
        {
            "id": "mock_7",
            "sender": "friend.alex@gmail.com",
            "sender_name": "Alex",
            "subject": "Weekend Plans?",
            "body": "Hey!\n\nWhat are you up to this weekend? Want to grab coffee or see a movie?\n\nLet me know!\nAlex",
            "timestamp": (base_time - timedelta(days=1, hours=5)).isoformat(),
            "labels": ["Personal"],
            "has_attachments": False,
            "is_read": False
        },
        {
            "id": "mock_8",
            "sender": "hr@company.com",
            "sender_name": "HR Department",
            "subject": "Performance Review Scheduled",
            "body": "Your annual performance review has been scheduled for March 20, 2024 at 10:00 AM. Please prepare a self-assessment document.\n\nLocation: HR Office, Room 301",
            "timestamp": (base_time - timedelta(days=4)).isoformat(),
            "labels": ["Work", "Important"],
            "has_attachments": False,
            "is_read": True
        },
        {
            "id": "mock_9",
            "sender": "spam@fake-winner.com",
            "sender_name": "Prize Winner",
            "subject": "You've Won $1,000,000!",
            "body": "Congratulations! You've won a million dollars! Click here to claim...",
            "timestamp": (base_time - timedelta(days=6)).isoformat(),
            "labels": ["Spam"],
            "has_attachments": False,
            "is_read": False
        },
        {
            "id": "mock_10",
            "sender": "project.manager@company.com",
            "sender_name": "Lisa Wang",
            "subject": "Project Milestone: Code Review Due",
            "body": "The code review for Sprint 3 is due by Friday, March 12. Please ensure all pull requests are reviewed and merged.\n\nKey areas to focus:\n- Security checks\n- Performance optimization\n- Documentation",
            "timestamp": (base_time - timedelta(days=2, hours=8)).isoformat(),
            "labels": ["Work", "To-Do"],
            "has_attachments": True,
            "attachments": [{"name": "review_checklist.docx", "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}],
            "is_read": False
        },
        {
            "id": "mock_11",
            "sender": "conference@techconf.org",
            "sender_name": "Tech Conference 2024",
            "subject": "Your Conference Registration Confirmed",
            "body": "Thank you for registering! Your conference pass is attached. Event dates: April 5-7, 2024.\n\nSee you there!",
            "timestamp": (base_time - timedelta(days=7)).isoformat(),
            "labels": ["Newsletter", "Event"],
            "has_attachments": True,
            "attachments": [{"name": "conference_pass.pdf", "type": "application/pdf"}],
            "is_read": True
        },
        {
            "id": "mock_12",
            "sender": "colleague@company.com",
            "sender_name": "David Kim",
            "subject": "Re: Database Schema Discussion",
            "body": "Thanks for your input on the schema design. I've updated the document with your suggestions. Can we discuss the indexing strategy in our next sync?\n\nBest,\nDavid",
            "timestamp": (base_time - timedelta(hours=6)).isoformat(),
            "labels": ["Work"],
            "has_attachments": False,
            "is_read": True
        },
        {
            "id": "mock_13",
            "sender": "bank@secure-bank.com",
            "sender_name": "Secure Bank",
            "subject": "Monthly Statement Available",
            "body": "Your monthly account statement is now available. Please review your transactions.",
            "timestamp": (base_time - timedelta(days=8)).isoformat(),
            "labels": ["Personal", "Finance"],
            "has_attachments": False,
            "is_read": True
        },
        {
            "id": "mock_14",
            "sender": "mentor@career.com",
            "sender_name": "Career Mentor",
            "subject": "Follow-up: Career Advice Session",
            "body": "Following up on our conversation, here are the resources I mentioned:\n1. Industry report\n2. Networking guide\n3. Interview prep materials\n\nLet's schedule another session next month.",
            "timestamp": (base_time - timedelta(days=3, hours=2)).isoformat(),
            "labels": ["Personal"],
            "has_attachments": True,
            "attachments": [
                {"name": "industry_report.pdf", "type": "application/pdf"},
                {"name": "networking_guide.pdf", "type": "application/pdf"}
            ],
            "is_read": False
        },
        {
            "id": "mock_15",
            "sender": "deadline.reminder@university.edu",
            "sender_name": "Course System",
            "subject": "Assignment 4 Due in 3 Days",
            "body": "Reminder: Assignment 4 for CS301 is due on March 13, 2024 at 11:59 PM. Don't forget to submit!",
            "timestamp": (base_time - timedelta(hours=1)).isoformat(),
            "labels": ["Work", "Deadline"],
            "has_attachments": False,
            "is_read": False
        }
    ]
    
    emails = []
    for item in sample_emails:
        email = Email(
            id=item["id"],
            sender=item["sender"],
            sender_name=item["sender_name"],
            subject=item["subject"],
            body=item["body"],
            timestamp=datetime.fromisoformat(item["timestamp"]),
            labels=item["labels"],
            has_attachments=item["has_attachments"],
            attachments=item.get("attachments", []),
            is_read=item.get("is_read", False)
        )
        emails.append(email)
    
    return emails

