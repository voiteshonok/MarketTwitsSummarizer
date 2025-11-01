"""Daily job scheduler for news processing and distribution."""

import asyncio
import subprocess
import sys
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..utils.config import config
from ..utils.logger import logger
from ..utils.redis_client import redis_client


class DailyJobScheduler:
    """Scheduler for daily news processing and distribution."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler(timezone=config.SCHEDULER_TIMEZONE)
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    async def dump_news_job(self):
        """Daily job to run standalone dumper process at 21:15."""
        try:
            logger.info("Starting daily news dump job at 21:15")
            
            # Run standalone dumper process
            logger.info("Running standalone dumper process...")
            result = await self.run_standalone_dumper()
            
            if result:
                logger.info("Daily news dump job completed successfully")
            else:
                logger.error("Daily news dump job failed")
            
        except Exception as e:
            logger.error(f"Daily news dump job failed: {e}")
    
    async def push_summary_job(self):
        """Daily job to push summaries to subscribers at 21:20."""
        try:
            logger.info("Starting daily summary push job at 21:20")
            
            # Get latest summary from Redis
            from ..models.schemas import Summary
            summary_data = redis_client.get_json("latest_summary")
            
            if not summary_data:
                logger.warning("No summary available to push to subscribers")
                return
            
            # Create Summary object
            summary = Summary(**summary_data)
            
            # Send summary to all subscribers
            logger.info(f"Pushing summary to subscribers: {summary.summary_text[:50]}...")
            from ..telegram_bot.bot import bot
            await bot.send_summary_to_subscribers(summary)
            
            logger.info("Daily summary push job completed successfully")
            
        except Exception as e:
            logger.error(f"Daily summary push job failed: {e}")
    
    async def run_standalone_dumper(self):
        """Run the standalone dumper process."""
        try:
            # Path to standalone dumper script
            dumper_script = os.path.join(self.project_root, "standalone_dumper.py")
            
            # Run the standalone dumper with daily flag
            process = await asyncio.create_subprocess_exec(
                sys.executable, dumper_script, "--daily",
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("Standalone dumper completed successfully")
                logger.info(f"Output: {stdout.decode()}")
                return True
            else:
                logger.error(f"Standalone dumper failed with return code {process.returncode}")
                logger.error(f"Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to run standalone dumper: {e}")
            return False
    
    
    def start_scheduler(self):
        """Start the scheduler."""
        try:
            # Schedule news dump job at 21:15
            self.scheduler.add_job(
                self.dump_news_job,
                trigger=CronTrigger(hour=22, minute=3, timezone=config.SCHEDULER_TIMEZONE),
                id="dump_news_job",
                name="Daily News Dump",
                replace_existing=True
            )
            
            # Schedule summary push job at 21:20
            self.scheduler.add_job(
                self.push_summary_job,
                trigger=CronTrigger(hour=22, minute=4, timezone=config.SCHEDULER_TIMEZONE),
                id="push_summary_job",
                name="Daily Summary Push",
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            logger.info(f"Scheduler started:")
            logger.info(f"  - News dump job scheduled for 21:48 {config.SCHEDULER_TIMEZONE}")
            logger.info(f"  - Summary push job scheduled for 21:49 {config.SCHEDULER_TIMEZONE}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    async def run_manual_dump_job(self):
        """Run the dump job manually (for testing)."""
        logger.info("Running manual dump job")
        await self.dump_news_job()
    
    async def run_manual_push_job(self):
        """Run the push job manually (for testing)."""
        logger.info("Running manual push job")
        await self.push_summary_job()
    
    async def run_manual_job(self):
        """Run both jobs manually (for testing)."""
        logger.info("Running manual jobs (dump + push)")
        await self.dump_news_job()
        await asyncio.sleep(2)  # Small delay between jobs
        await self.push_summary_job()


# Global scheduler instance
scheduler = DailyJobScheduler()