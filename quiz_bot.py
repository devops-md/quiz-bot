from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot, Poll
from telegram.constants import ParseMode
import asyncio, os, urllib.request, json, random

# import datetime

BOT_TOKEN = os.environ.get('BOT_TOKEN') 
CHANNEL_ID = os.environ.get('CHANNEL_ID')
THREAD_ID = os.environ.get('THREAD_ID')
MCQ_URL = os.environ.get('MCQ_URL', "https://raw.githubusercontent.com/devops-md/quiz-bot/refs/heads/main/questions.json")
PUBLISH_TIME = os.environ.get('PUBLISH_TIME', "8:55")
DAILY_QUIZES = int(os.environ.get('DAILY_QUIZES',"1"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ["true", "1", "yes", "y", "on"]

async def publish_quiz(bot: Bot):
    """Publishes a quiz to the specified channel."""

    with urllib.request.urlopen(MCQ_URL) as url:
        quizes = json.load(url)
        # today_index = datetime.datetime.now().timetuple().tm_yday % len(quizes)
        # today_index = random.randint(0,len(quizes)-1)
        for _ in range(DAILY_QUIZES):
            quiz = random.choice(quizes)
            correct_response = quiz["options"][quiz["correct_option_id"]]
            random.shuffle(quiz["options"])
            quiz["correct_option_id"] = quiz["options"].index(correct_response)
        
            await bot.send_poll(
                chat_id=CHANNEL_ID,
                message_thread_id=THREAD_ID,
                question=quiz["question"],
                options=quiz["options"],
                type=Poll.QUIZ,
                correct_option_id=quiz["correct_option_id"],
                explanation=quiz["explanation"],
                is_anonymous=True,
                explanation_parse_mode=ParseMode.MARKDOWN
            )

async def main():
    # Initialize the bot and scheduler
    bot = Bot(token=BOT_TOKEN)
    if DEBUG_MODE:
        await publish_quiz(bot)
    scheduler = BackgroundScheduler()
    scheduler.add_job(publish_quiz, 'cron', hour=int(PUBLISH_TIME.split(":")[0]), minute=int(PUBLISH_TIME.split(":")[1]), args=[bot])

    scheduler.start()

    print("Quiz bot is running...")
    # Keep the bot running
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
