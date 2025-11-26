"""
Prompt storage and persistence.

Handles saving and loading prompts to/from JSON file.
"""
import json
import os
from typing import Dict
from core import prompts
import config


PROMPTS_FILE = os.path.join(config.DATA_DIR, "prompts.json")


def load_prompts() -> Dict[str, str]:
    """
    Load prompts from JSON file, or return defaults if file doesn't exist.
    
    Returns:
        Dictionary of prompt templates
    """
    if os.path.exists(PROMPTS_FILE):
        try:
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                saved_prompts = json.load(f)
                # Merge with defaults to ensure all prompts exist
                default_prompts = get_default_prompts()
                default_prompts.update(saved_prompts)
                return default_prompts
        except Exception as e:
            print(f"Error loading prompts from file: {e}")
            return get_default_prompts()
    else:
        return get_default_prompts()


def save_prompts(prompts_dict: Dict[str, str]):
    """
    Save prompts to JSON file.
    
    Args:
        prompts_dict: Dictionary of prompt templates
    """
    try:
        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)
        
        with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(prompts_dict, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise Exception(f"Error saving prompts: {e}")


def get_default_prompts() -> Dict[str, str]:
    """
    Get default prompt templates.
    
    Returns:
        Dictionary of default prompt templates
    """
    return {
        'categorization': prompts.CATEGORIZATION_PROMPT,
        'task_extraction': prompts.TASK_EXTRACTION_PROMPT,
        'event_extraction': prompts.EVENT_EXTRACTION_PROMPT,
        'reply_generation': prompts.REPLY_GENERATION_PROMPT,
        'new_draft_generation': prompts.NEW_DRAFT_GENERATION_PROMPT,
        'explanation': prompts.EXPLANATION_PROMPT,
        'tone_check': prompts.REPLY_TONE_CHECK_PROMPT,
        'sender_context': prompts.SENDER_CONTEXT_PROMPT,
        'inbox_query': prompts.INBOX_QUERY_PROMPT
    }

