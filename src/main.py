"""Main entry point for DevOps Moldova Quiz Bot."""

import asyncio
import logging
import signal
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.config import settings
from src.quiz_service import QuizService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("quiz_bot")


async def main() -> None:
    """Bootstraps the scheduler and runs the quiz bot event loop."""
    logger.info("Initializing DevOps Moldova Quiz Bot...")
    logger.info(f"Ollama Target URL: {settings.ollama_base_url} (Model: {settings.ollama_model})")
    logger.info(f"Target Timezone: {settings.tz} | Daily Schedule: {settings.publish_time}")
    logger.info(f"Debug Mode: {settings.debug_mode}")

    service = QuizService(settings)
    scheduler = AsyncIOScheduler(timezone=settings.tz)

    if settings.debug_mode:
        logger.info(
            f"DEBUG MODE ACTIVE: scheduling quiz every {settings.debug_interval_minutes} minute(s)."
        )
        scheduler.add_job(
            service.execute_daily_quiz,
            trigger=IntervalTrigger(minutes=settings.debug_interval_minutes),
            id="debug_quiz_job",
            name="Debug Quiz Job",
            replace_existing=True,
        )
        # In debug mode, also fire one question 5 seconds after startup for immediate check
        asyncio.get_event_loop().call_later(
            5, lambda: asyncio.create_task(service.execute_daily_quiz())
        )

    # Production daily cron job
    cron_trigger = CronTrigger(
        hour=settings.publish_hour,
        minute=settings.publish_minute,
        timezone=settings.tz,
    )
    scheduler.add_job(
        service.execute_daily_quiz,
        trigger=cron_trigger,
        id="daily_quiz_job",
        name="Daily Quiz Job",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started successfully. Waiting for scheduled events...")

    stop_event = asyncio.Event()

    def handle_shutdown(signum, frame):
        logger.info(f"Received exit signal ({signum}). Shutting down gracefully...")
        scheduler.shutdown(wait=False)
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, handle_shutdown)
        except (ValueError, AttributeError):
            # Not supported in non-main threads or some environments
            pass

    try:
        await stop_event.wait()
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        logger.info("Quiz Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
