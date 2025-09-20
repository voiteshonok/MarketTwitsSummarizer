#!/usr/bin/env python3
"""Standalone dumper process that stores summaries directly in Redis."""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import config
from src.utils.logger import logger
from src.dumper.telegram_dumper import TelegramDumper
from src.llm_module.summarizer import NewsSummarizer
from src.utils.redis_client import redis_client


class StandaloneDumper:
    """Standalone dumper that stores summaries directly in Redis."""
    
    def __init__(self):
        """Initialize the standalone dumper."""
        self.dumper = TelegramDumper()
        self.summarizer = NewsSummarizer()
        
    async def dump_and_summarize(self, days_ago: int = 1) -> bool:
        """Dump news and create summary, storing in Redis."""
        try:
            logger.info(f"Starting dump and summarize process (days_ago={days_ago})")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_ago)
            
            # Dump news
            logger.info("Dumping news from Telegram...")
            success = await self.dumper.dump_news(from_date=start_date)
            
            if not success:
                logger.error("Failed to dump news")
                return False
            
            # Get news for the date
            news_batch = self.dumper.get_news_for_date(end_date.date())
            if not news_batch or not news_batch.items:
                logger.warning("No news found for the specified date")
                return False
            
            # Create summary
            logger.info("Creating summary...")
            summary = await self.summarizer.summarize_news(news_batch)
            
            if not summary:
                logger.error("Failed to create summary")
                return False
            
            # Store summary in Redis
            logger.info("Storing summary in Redis...")
            success = await self.store_summary_in_redis(summary)
            
            if success:
                logger.info(f"Successfully stored summary: {summary.summary_text[:50]}...")
                return True
            else:
                logger.error("Failed to store summary in Redis")
                return False
            
        except Exception as e:
            logger.error(f"Error in dump_and_summarize: {e}")
            return False
        finally:
            # Close dumper connection
            await self.dumper.close()
    
    async def store_summary_in_redis(self, summary) -> bool:
        """Store summary in Redis."""
        try:
            # Store by date
            date_str = summary.date.strftime('%Y%m%d')
            redis_key = f"summary:{date_str}"
            redis_client.set(redis_key, summary.model_dump())
            
            # Store as latest summary
            redis_client.set("latest_summary", summary.model_dump())
            
            # Store in summaries list
            summaries_key = "summaries"
            redis_client.add_to_set(summaries_key, date_str)
            
            logger.info(f"Summary stored with key: {redis_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store summary in Redis: {e}")
            return False
    
    async def run_daily_process(self):
        """Run the complete daily process."""
        try:
            logger.info("Starting daily dumper process...")
            
            # Dump and summarize
            success = await self.dump_and_summarize(days_ago=1)
            
            if success:
                logger.info("Daily process completed successfully")
                return True
            else:
                logger.error("Daily process failed")
                return False
                
        except Exception as e:
            logger.error(f"Error in daily process: {e}")
            return False


async def main():
    """Main entry point for standalone dumper."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standalone MarketTwits Dumper")
    parser.add_argument("--days-ago", type=int, default=1, help="Number of days ago to dump")
    parser.add_argument("--daily", action="store_true", help="Run daily process")
    args = parser.parse_args()
    
    logger.info("Starting standalone dumper...")
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    dumper = StandaloneDumper()
    
    try:
        if args.daily:
            # Run daily process
            success = await dumper.run_daily_process()
            if success:
                logger.info("Daily process completed successfully")
                sys.exit(0)
            else:
                logger.error("Daily process failed")
                sys.exit(1)
        else:
            # Run single dump
            success = await dumper.dump_and_summarize(days_ago=args.days_ago)
            if success:
                logger.info("Dump and summarize completed successfully")
            else:
                logger.error("Dump and summarize failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
