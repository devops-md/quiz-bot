"""
Web JSON provider for quiz data.
Fetches quiz questions from a JSON file hosted on the web.
"""

import logging
import os
import random
import requests

logger = logging.getLogger(__name__)

# Configuration
JSON_URL = os.environ.get(
    'MCQ_URL',
    "https://raw.githubusercontent.com/devops-md/quiz-bot/refs/heads/main/questions.json"
)


def fetch_quiz_from_json(json_url=None):
    """
    Fetch quiz data from a JSON URL and prepare a random quiz.
    
    Args:
        json_url: URL to fetch quiz questions from. If None, uses JSON_URL from config.
        
    Returns:
        Dictionary containing question, options, correct_option_id, and explanation
        
    Raises:
        requests.exceptions.RequestException: If there's an error fetching the data
        KeyError: If the JSON data is missing required fields
    """
    url = json_url or JSON_URL
    logger.info(f"Fetching quiz from JSON: {url}")
    
    response = requests.get(url)
    response.raise_for_status()  # Raise HTTPError for bad responses

    quizes = response.json()
    quiz = random.choice(quizes)

    # Validate required fields
    required_fields = ["question", "options", "correct_option_id", "explanation"]
    for field in required_fields:
        if field not in quiz:
            raise KeyError(f"JSON data missing required field: {field}")

    # Shuffle options while maintaining correct answer
    correct_response = quiz["options"][quiz["correct_option_id"]]
    random.shuffle(quiz["options"])
    quiz["correct_option_id"] = quiz["options"].index(correct_response)

    return quiz
