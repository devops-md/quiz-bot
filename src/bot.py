"""
Telegram bot functionality module.
Handles bot initialization and message sending.
"""

import logging
import os
from telegram import Bot, Poll

logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
THREAD_ID = os.environ.get('THREAD_ID')

# Initialize the bot
bot = Bot(token=BOT_TOKEN)


async def send_quiz_to_channel(quiz_poll):
    """
    Send a quiz poll to the configured Telegram channel.
    
    Args:
        quiz_poll: Dictionary containing question, options, correct_option_id, and explanation
        
    Raises:
        Exception: If there's an error sending the poll
    """
    await bot.send_poll(
        chat_id=CHANNEL_ID,
        message_thread_id=THREAD_ID,
        question=quiz_poll["question"],
        options=quiz_poll["options"],
        type=Poll.QUIZ,
        correct_option_id=quiz_poll["correct_option_id"],
        explanation=quiz_poll["explanation"],
        is_anonymous=True
    )
    logger.info("Quiz poll sent successfully to the channel.")
