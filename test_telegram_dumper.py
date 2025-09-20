"""Test script for the new Telethon-based dumper."""

import asyncio
import os
from datetime import datetime, timedelta

# Set up environment for testing
os.environ['TELEGRAM_API_ID'] = 'test_api_id'
os.environ['TELEGRAM_API_HASH'] = 'test_api_hash'
os.environ['TELEGRAM_CHANNEL_USERNAME'] = 'MarketTwits'
os.environ['TELEGRAM_SESSION_NAME'] = 'test_session'

from src.dumper.telegram_dumper import TelegramDumper
from src.utils.logger import logger


async def test_dumper():
    """Test the Telegram dumper functionality."""
    logger.info("Testing Telegram dumper...")
    
    # Initialize dumper
    dumper = TelegramDumper()
    
    # Test file operations
    logger.info("Testing file operations...")
    
    # Test news count
    count = dumper.get_news_count()
    logger.info(f"Current news count: {count}")
    
    # Test getting all news
    all_news = dumper.get_all_news()
    logger.info(f"Retrieved {len(all_news)} news items")
    
    # Test getting news for a specific date
    yesterday = datetime.now() - timedelta(days=1)
    news_batch = dumper.get_news_for_date(yesterday)
    if news_batch:
        logger.info(f"Found {len(news_batch.items)} news items for {yesterday.date()}")
    else:
        logger.info(f"No news found for {yesterday.date()}")
    
    # Test loading latest timestamp
    latest_timestamp = dumper.load_latest_timestamp()
    logger.info(f"Latest timestamp: {latest_timestamp}")
    
    logger.info("Dumper test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_dumper())
