"""
Quiz functionality module.
Handles quiz data processing and orchestration.
"""

import logging
import os

from src.bot import send_quiz_to_channel
from src.provider_webjson import fetch_quiz_from_json
from src.provider_quizapi import fetch_quiz_from_quizapi

logger = logging.getLogger(__name__)

# Configuration
QUIZ_SOURCE = os.environ.get('QUIZ_SOURCE', 'json').lower()  # 'json' or 'quizapi'


def create_quiz_poll(question_data):
    """
    Create a quiz poll from question data with Telegram API limitations applied.
    
    Telegram Quiz Poll Limitations:
    - Question: 1-300 characters
    - Options: 2-10 options, each 1-100 characters
    - Explanation: 0-200 characters
    
    Args:
        question_data: Dictionary containing question, options, correct_option_id, and explanation
        
    Returns:
        Dictionary with formatted quiz poll data
        
    Raises:
        ValueError: If data doesn't meet minimum requirements
    """
    question = question_data["question"]
    options = question_data["options"]
    correct_option_id = question_data["correct_option_id"]
    explanation = question_data.get("explanation", "")
    
    # Validate and trim question (1-300 characters)
    if not question:
        raise ValueError("Question cannot be empty")
    if len(question) > 300:
        question = question[:297] + "..."
        logger.warning(f"Question truncated to 300 characters")
    
    # Validate and trim options (2-10 options, each 1-100 characters)
    if len(options) < 2:
        raise ValueError("Quiz must have at least 2 options")
    if len(options) > 10:
        logger.warning(f"Too many options ({len(options)}), keeping first 10")
        # If correct answer is beyond 10th option, this is a problem
        if correct_option_id >= 10:
            raise ValueError("Correct option is beyond the 10 option limit")
        options = options[:10]
    
    # Trim each option to 100 characters
    trimmed_options = []
    for i, option in enumerate(options):
        if not option or len(option.strip()) == 0:
            raise ValueError(f"Option {i+1} cannot be empty")
        if len(option) > 100:
            trimmed_option = option[:97] + "..."
            logger.warning(f"Option {i+1} truncated to 100 characters")
            trimmed_options.append(trimmed_option)
        else:
            trimmed_options.append(option)
    
    # Validate correct_option_id
    if correct_option_id < 0 or correct_option_id >= len(trimmed_options):
        raise ValueError(f"Invalid correct_option_id: {correct_option_id}")
    
    # Build explanation with correct answer prefix (max 200 characters total)
    correct_answer_text = trimmed_options[correct_option_id]
    explanation_prefix = f"✓ {correct_answer_text}\n"
    
    # Calculate remaining space for explanation
    remaining_space = 200 - len(explanation_prefix)
    
    if explanation and len(explanation) > 0:
        if len(explanation) > remaining_space:
            explanation = explanation[:remaining_space-3] + "..."
            logger.warning(f"Explanation truncated to fit 200 character limit")
        formatted_explanation = explanation_prefix + explanation
    else:
        formatted_explanation = explanation_prefix.rstrip()
    
    # Final check
    if len(formatted_explanation) > 200:
        formatted_explanation = formatted_explanation[:197] + "..."

    # Format the quiz message
    return {
        "question": question,
        "options": trimmed_options,
        "correct_option_id": correct_option_id,
        "explanation": formatted_explanation
    }


def fetch_quiz_data_from_source():
    """
    Fetch quiz data from the configured source (JSON or API).
    
    Returns:
        Dictionary with quiz data (question, options, correct_option_id, explanation)
        
    Raises:
        requests.exceptions.RequestException: If there's an error fetching the data
        ValueError: If QUIZ_SOURCE is invalid
    """
    if QUIZ_SOURCE == 'quizapi':
        return fetch_quiz_from_quizapi()
    elif QUIZ_SOURCE == 'json':
        return fetch_quiz_from_json()
    else:
        raise ValueError(f"Invalid QUIZ_SOURCE: {QUIZ_SOURCE}. Must be 'json' or 'quizapi'")


async def process_quiz():
    """
    Fetch quiz data from the configured source and send it to the Telegram channel.
        
    Raises:
        Exception: If there's an error fetching or sending the quiz
    """
    try:
        quiz_data = fetch_quiz_data_from_source()
        quiz_poll = create_quiz_poll(quiz_data)
        await send_quiz_to_channel(quiz_poll)
    except Exception as e:
        logger.error(f"Error processing quiz: {e}")
        raise

