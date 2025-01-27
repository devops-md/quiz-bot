import asyncio, os, random, requests, logging
from telegram import Bot, Poll
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Replace with your bot token and channel username
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
THREAD_ID = os.environ.get('THREAD_ID')
JSON_URL = os.environ.get('MCQ_URL', "https://raw.githubusercontent.com/devops-md/quiz-bot/refs/heads/main/questions.json")
PUBLISH_TIME = os.environ.get('PUBLISH_TIME', "8:55")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ["true", "1", "yes", "y", "on"]

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize the bot
bot = Bot(token=BOT_TOKEN)

async def fetch_and_send_json():
    """Fetch JSON from a URL and send it to the Telegram channel."""
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()  # Raise HTTPError for bad responses

        quizes = response.json()
        quiz = random.choice(quizes)

        correct_response = quiz["options"][quiz["correct_option_id"]]
        random.shuffle(quiz["options"])
        quiz["correct_option_id"] = quiz["options"].index(correct_response)

        # Send the JSON data to the channel
        # await bot.send_message( 
        #             chat_id=CHANNEL_ID,
        #             message_thread_id=THREAD_ID, text=quiz)
        await bot.send_poll(
                    chat_id=CHANNEL_ID,
                    message_thread_id=THREAD_ID,
                    question=quiz["question"],
                    options=quiz["options"],
                    type=Poll.QUIZ,
                    correct_option_id=quiz["correct_option_id"],
                    explanation=quiz["explanation"],
                    is_anonymous=True
                )
        logger.info("Quiz sent successfully to the channel.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

async def main():
    """Main entry point of the bot."""
    # Set up the scheduler
    scheduler = AsyncIOScheduler()

    if DEBUG_MODE:
      # Add a job to the scheduler each minute
      scheduler.add_job(fetch_and_send_json, "interval", minutes=1)

    # Add a job to the scheduler at specified time
    scheduler.add_job(
        fetch_and_send_json,
        'cron',
        hour=int(PUBLISH_TIME.split(":")[0]),
        minute=int(PUBLISH_TIME.split(":")[1])
    )

    scheduler.start()
    logger.info("Bot started. It will fetch and send Quiz daily.")

    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Bot stopped.")

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())