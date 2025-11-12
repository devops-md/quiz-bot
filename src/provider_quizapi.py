"""
Quiz API provider for quiz data.
Fetches quiz questions from an API endpoint.
"""

import logging
import os
import random
import requests

logger = logging.getLogger(__name__)

# Configuration
API_ENDPOINT = os.environ.get(
    'QUIZAPI_ENDPOINT',
    "https://quizapi.io/api/v1/questions" # /ai for ai generated Max 5/day
)
API_KEY = os.environ.get('QUIZAPI_KEY', '')  # Your QuizAPI.io API key
DIFFICULTY = os.environ.get('DIFFICULTY', "hard") # Difficulty level: easy, medium, hard

# Quiz categories
CATEGORIES = [
     "Linux",
     "bash",
     "uncategorized",
     "Docker",
     "SQL",
    #  "CMS",
     "Code",
     "DevOps",
    #  "React",
    #  "Laravel",
     "Postgres",
    #  "Django",
    #  "cPanel",
    #  "NodeJs",
    #  "WordPress",
    #  "Next.js",
    #  "VueJS",
     "Apache Kafka",
    #  "HTML",
]


def fetch_quiz_from_quizapi(api_endpoint=None):
    """
    Fetch a single quiz from QuizAPI.io endpoint.
    
    Args:
        api_endpoint: API endpoint URL that returns quiz questions.
                     If None, uses API_ENDPOINT from config.
        
    Returns:
        Dictionary containing question, options, correct_option_id, and explanation
        
    Raises:
        requests.exceptions.RequestException: If there's an error fetching the data
        ValueError: If API_KEY is not set or response is invalid
    """
    if not API_KEY:
        raise ValueError("QUIZAPI_KEY environment variable must be set")
    
    url = api_endpoint or API_ENDPOINT
    
    # Select a random category
    category = random.choice(CATEGORIES)
    
    # Prepare request
    headers = {
        'X-Api-Key': API_KEY
    }
    
    payload = {
        'limit': 1,
        'difficulty': DIFFICULTY,
        'category': category
    }
    
    logger.info(f"Fetching quiz from QuizAPI: category={category}, difficulty={DIFFICULTY}")
    
    # Keep fetching until we get a question with single correct answer
    max_attempts = 5
    for attempt in range(max_attempts):
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses

        quiz_array = response.json()
        
        if not quiz_array or len(quiz_array) == 0:
            raise ValueError("QuizAPI returned empty response")
        
        quiz_data = quiz_array[0]
        
        # Check if question has multiple correct answers
        multiple_correct = quiz_data.get('multiple_correct_answers', 'false')
        if multiple_correct != "false":
            logger.info(f"Question has multiple correct answers, fetching another (attempt {attempt + 1}/{max_attempts})")
            continue  # Fetch another question
        
        # Extract answers and find correct one
        answers = quiz_data.get('answers', {})
        correct_answers = quiz_data.get('correct_answers', {})
        
        # Build options list and find correct answer
        options = []
        correct_option_id = None
        
        for key in ['answer_a', 'answer_b', 'answer_c', 'answer_d', 'answer_e', 'answer_f']:
            answer_text = answers.get(key)
            if answer_text:  # Only include non-null answers
                options.append(answer_text)
                # Check if this is the correct answer
                correct_key = f"{key}_correct"
                if correct_answers.get(correct_key) == "true":
                    correct_option_id = len(options) - 1
        
        if correct_option_id is None:
            raise ValueError("No correct answer found in QuizAPI response")
        
        # Shuffle options while maintaining correct answer
        correct_response = options[correct_option_id]
        random.shuffle(options)
        correct_option_id = options.index(correct_response)
        
        # Build explanation
        explanation = quiz_data.get('explanation') or quiz_data.get('tip') or "No explanation provided"
        
        return {
            "question": quiz_data.get('question'),
            "options": options,
            "correct_option_id": correct_option_id,
            "explanation": explanation
        }
    
    # If we've exhausted all attempts
    raise ValueError(f"Could not find a question with single correct answer after {max_attempts} attempts")


