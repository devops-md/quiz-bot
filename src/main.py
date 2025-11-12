"""
Main entry point for the Quiz Bot application.
Handles startup, scheduling, and orchestration.
"""

import asyncio
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.quiz import process_quiz

# Configuration
PUBLISH_TIME = os.environ.get('PUBLISH_TIME', "8:55")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ["true", "1", "yes", "y", "on"]

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    """Main entry point of the bot."""
    # Set up the scheduler
    scheduler = AsyncIOScheduler()
    
    if DEBUG_MODE:
        # Add a job to the scheduler each minute for debugging
        scheduler.add_job(process_quiz, "interval", minutes=1)
        logger.info("DEBUG MODE: Quiz will be sent every minute")

    # Add a job to the scheduler at specified time
    scheduler.add_job(
        process_quiz,
        'cron',
        hour=int(PUBLISH_TIME.split(":")[0]),
        minute=int(PUBLISH_TIME.split(":")[1])
    )

    scheduler.start()

    logger.info(f"Bot started. Quiz will be sent daily at {PUBLISH_TIME}.")

    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
