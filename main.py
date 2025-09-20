"""Main application entry point for MarketTwits Summarizer."""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.utils.config import config
from src.utils.logger import logger
from src.telegram_server.api import app
from src.scheduler.daily_job import scheduler
from src.telegram_bot.bot import bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting MarketTwits Summarizer application")
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Start scheduler
        scheduler.start_scheduler()
        logger.info("Scheduler started successfully")
        
        # Start Telegram bot
        await bot.start_bot()
        logger.info("Telegram bot started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)
    
    # Shutdown
    logger.info("Shutting down MarketTwits Summarizer application")
    await bot.stop_bot()
    scheduler.stop_scheduler()
    
    # Close dumper connection
    # from src.dumper.telegram_dumper import TelegramDumper
    # dumper = TelegramDumper()
    # # await dumper.close()
    
    logger.info("Application shutdown complete")


# Set the lifespan
app.router.lifespan_context = lifespan


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    scheduler.stop_scheduler()
    sys.exit(0)


def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
