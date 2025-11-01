"""Command-line interface for MarketTwits Summarizer."""

import asyncio
import argparse
from datetime import datetime, timedelta

from src.dumper.telegram_dumper import TelegramDumper
from src.llm_module.summarizer import NewsSummarizer
from src.utils.logger import logger
from src.utils.config import config


async def dump_news(from_days_ago: int = 1):
    """Dump news from Telegram channel."""
    logger.info(f"Dumping news from {from_days_ago} days ago")
    
    dumper = TelegramDumper()
    from_date = datetime.now() - timedelta(days=from_days_ago)
    
    success = await dumper.dump_news(from_date)
    if success:
        logger.info("News dump completed successfully")
    else:
        logger.error("News dump failed")


async def create_summary(target_date: str = None):
    """Create summary for a specific date."""
    if target_date:
        try:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD")
            return
    else:
        date_obj = datetime.now() - timedelta(days=1)
    
    logger.info(f"Creating summary for {date_obj.date()}")
    
    dumper = TelegramDumper()
    summarizer = NewsSummarizer()
    
    # Get news batch
    news_batch = dumper.get_news_for_date(date_obj)
    if not news_batch:
        logger.error(f"No news found for {date_obj.date()}")
        return
    
    # Create summary
    summary = await summarizer.process_news_batch(news_batch)
    if summary:
        logger.info("Summary created successfully")
        print(f"\nSummary for {summary.date}:")
        print(f"News count: {summary.news_count}")
        print(f"Summary: {summary.summary_text}")
        print(f"Key topics: {', '.join(summary.key_topics)}")
    else:
        logger.error("Failed to create summary")


async def show_news_stats():
    """Show news statistics."""
    logger.info("Getting news statistics")
    
    dumper = TelegramDumper()
    total_count = dumper.get_news_count()
    
    print(f"\nNews Statistics:")
    print(f"Total news items: {total_count}")
    
    # Show recent news items
    all_news = dumper.get_all_news()
    if all_news:
        print(f"\nMost recent news items:")
        for i, item in enumerate(all_news[-5:], 1):  # Show last 5 items
            print(f"{i}. [{item.date.strftime('%Y-%m-%d %H:%M')}] {item.text[:100]}...")
    else:
        print("No news items found")


async def run_daily_job():
    """Run both daily jobs manually."""
    logger.info("Running both daily jobs manually")
    
    from src.scheduler.daily_job import scheduler
    await scheduler.run_manual_job()


async def run_dump_job():
    """Run the dump job manually."""
    logger.info("Running dump job manually")
    
    from src.scheduler.daily_job import scheduler
    await scheduler.run_manual_dump_job()


async def run_push_job():
    """Run the push job manually."""
    logger.info("Running push job manually")
    
    from src.scheduler.daily_job import scheduler
    await scheduler.run_manual_push_job()


async def clear_latest_summary():
    """Clear the latest summary from Redis."""
    logger.info("Clearing latest summary from Redis...")
    
    try:
        from src.utils.redis_client import redis_client
        
        # Clear latest summary
        result = redis_client.delete("latest_summary")
        
        if result:
            logger.info("✅ Latest summary cleared successfully")
            print("✅ Latest summary cleared from Redis")
        else:
            logger.warning("No latest summary found to clear")
            print("ℹ️  No latest summary found to clear")
            
    except Exception as e:
        logger.error(f"Failed to clear latest summary: {e}")
        print(f"❌ Failed to clear latest summary: {e}")


async def clear_summary_by_date(target_date: str = None):
    """Clear summary for a specific date."""
    if not target_date:
        print("❌ Please provide a date in YYYY-MM-DD format")
        return
    
    try:
        from datetime import datetime
        from src.utils.redis_client import redis_client
        
        # Parse date
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        date_str = date_obj.strftime('%Y%m%d')
        
        logger.info(f"Clearing summary for {target_date}...")
        
        # Clear summary for specific date
        redis_key = f"summary:{date_str}"
        result = redis_client.delete(redis_key)
        
        if result:
            logger.info(f"✅ Summary for {target_date} cleared successfully")
            print(f"✅ Summary for {target_date} cleared from Redis")
        else:
            logger.warning(f"No summary found for {target_date}")
            print(f"ℹ️  No summary found for {target_date}")
            
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2024-01-15)")
    except Exception as e:
        logger.error(f"Failed to clear summary for {target_date}: {e}")
        print(f"❌ Failed to clear summary for {target_date}: {e}")


async def preview_news(days_ago: int = 1, limit: int = 10):
    """Preview news items that would go to summarization."""
    logger.info(f"Previewing news for {days_ago} days ago, limit {limit}")
    
    try:
        import requests
        from src.utils.config import config
        
        # Use localhost instead of 0.0.0.0 for local connections
        host = "localhost" if config.HOST == "0.0.0.0" else config.HOST
        response = requests.get(
            f"http://{host}:{config.PORT}/news/preview",
            params={"days_ago": days_ago, "limit": limit},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print(f"✅ News preview for {data['date']}")
                print(f"📊 Total available: {data['total_available']}")
                print(f"👀 Preview count: {data['preview_count']}")
                print("\n📰 News Items:")
                print("=" * 50)
                
                for i, item in enumerate(data["news_items"], 1):
                    print(f"{i}. [ID: {item['id']}] {item['text'][:100]}...")
                    print(f"   📅 {item['date']} | 👀 {item['views']} | 🔄 {item['forwards']}")
                    print()
                
                return True
            else:
                print(f"ℹ️  {data['message']}")
                return False
        else:
            print(f"❌ Failed to get news preview: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running.")
        return False
    except Exception as e:
        logger.error(f"Failed to preview news: {e}")
        print(f"❌ Failed to preview news: {e}")
        return False


async def preview_summarization(days_ago: int = 1):
    """Preview what would be sent to AI for summarization."""
    logger.info(f"Previewing summarization for {days_ago} days ago")
    
    try:
        import requests
        from src.utils.config import config
        
        # Use localhost instead of 0.0.0.0 for local connections
        host = "localhost" if config.HOST == "0.0.0.0" else config.HOST
        response = requests.get(
            f"http://{host}:{config.PORT}/news/summarization-preview",
            params={"days_ago": days_ago},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print(f"✅ Summarization preview for {data['date']}")
                print(f"📊 News count: {data['news_count']}")
                print(f"📝 Text count: {data['text_count']}")
                print(f"📏 Total text length: {data['total_text_length']}")
                print(f"✂️  Truncated: {'Yes' if data['truncated'] else 'No'}")
                
                print("\n📰 Sample News:")
                print("=" * 50)
                for i, item in enumerate(data["sample_news"], 1):
                    print(f"{i}. [ID: {item['id']}] {item['text']}")
                    print(f"   📅 {item['date']}")
                    print()
                
                print("\n🤖 AI Prompt Preview:")
                print("=" * 50)
                print(data["prompt_preview"][:500] + "..." if len(data["prompt_preview"]) > 500 else data["prompt_preview"])
                
                return True
            else:
                print(f"ℹ️  {data['message']}")
                return False
        else:
            print(f"❌ Failed to get summarization preview: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running.")
        return False
    except Exception as e:
        logger.error(f"Failed to preview summarization: {e}")
        print(f"❌ Failed to preview summarization: {e}")
        return False


async def clear_news_data():
    """Clear all news data from storage and Redis."""
    logger.info("Clearing all news data...")
    
    try:
        import os
        from src.utils.config import config
        from src.utils.redis_client import redis_client
        
        # Clear the news file
        news_file = os.path.join(config.DATA_DIR, "all_news.json")
        if os.path.exists(news_file):
            # Create backup
            backup_file = news_file + ".backup"
            os.rename(news_file, backup_file)
            logger.info(f"Backed up news file to {backup_file}")
        
        # Recreate empty news file
        from src.dumper.telegram_dumper import TelegramDumper
        dumper = TelegramDumper()
        dumper._initialize_news_file()
        
        # Clear Redis data
        logger.info("Clearing Redis cache...")
        redis_keys_to_clear = [
            "all_news",                    # Main news data
            "latest_news_timestamp",       # Latest news timestamp
            "latest_summary",              # Latest summary
        ]
        
        # Clear summary keys (format: summary:YYYYMMDD)
        # We'll get all keys matching the pattern and delete them
        try:
            # Get all keys matching summary pattern
            all_keys = redis_client.redis_client.keys("summary:*")
            redis_keys_to_clear.extend(all_keys)
        except Exception as e:
            logger.warning(f"Could not get summary keys from Redis: {e}")
        
        # Delete all identified keys
        cleared_count = 0
        for key in redis_keys_to_clear:
            if redis_client.delete(key):
                cleared_count += 1
                logger.debug(f"Cleared Redis key: {key}")
        
        logger.info(f"Cleared {cleared_count} keys from Redis")
        
        logger.info("✅ All news data cleared successfully")
        print("✅ All news data cleared successfully")
        print("ℹ️  News file backed up before clearing")
        print(f"ℹ️  Cleared {cleared_count} keys from Redis cache")
        
    except Exception as e:
        logger.error(f"Failed to clear news data: {e}")
        print(f"❌ Failed to clear news data: {e}")


async def generate_fresh_summary(days_ago: int = 1):
    """Generate fresh summary without caching."""
    logger.info(f"Generating fresh summary for {days_ago} days ago")
    
    try:
        import requests
        from src.utils.config import config
        
        # Use localhost instead of 0.0.0.0 for local connections
        host = "localhost" if config.HOST == "0.0.0.0" else config.HOST
        response = requests.post(
            f"http://{host}:{config.PORT}/news/generate-summary",
            params={"days_ago": days_ago},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                summary = data["summary"]
                print(f"✅ Fresh summary generated for {summary['date']}")
                print(f"📊 News count: {data['news_count']}")
                print(f"⏰ Generated at: {data['generated_at']}")
                print(f"\n📝 Summary:")
                print("=" * 50)
                print(summary['summary_text'])
                
                if summary.get('key_topics'):
                    key_topics = '\n'.join(summary['key_topics'])
                    print(f"\n🔑 Key Topics: {key_topics}")
                
                return True
            else:
                print(f"❌ Failed to generate summary: {data['message']}")
                return False
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running.")
        return False
    except Exception as e:
        logger.error(f"Failed to generate fresh summary: {e}")
        print(f"❌ Failed to generate fresh summary: {e}")
        return False


async def test_bot():
    """Test the Telegram bot functionality."""
    logger.info("Testing Telegram bot...")
    
    from src.telegram_bot.bot import bot
    
    try:
        # Test bot connection first
        bot_info = await bot.bot.get_me()
        logger.info(f"Bot connected: {bot_info.first_name} (@{bot_info.username})")
        
        # Check webhook
        webhook_info = await bot.bot.get_webhook_info()
        if webhook_info.url:
            logger.info("Webhook detected, deleting it...")
            await bot.bot.delete_webhook()
            logger.info("Webhook deleted successfully")
        else:
            logger.info("No webhook set - polling should work")
        
        # Start bot
        await bot.start_bot()
        logger.info("Bot started successfully")
        
        # Get subscriber count
        from src.utils.redis_client import redis_client
        subscribers = redis_client.get_set_members("subscribers")
        logger.info(f"Current subscribers: {len(subscribers)}")
        
        # Wait a bit for testing
        logger.info("Bot is running for 10 seconds for testing...")
        await asyncio.sleep(10)
        
        # Stop bot
        await bot.stop_bot()
        logger.info("Bot stopped successfully")
        
    except Exception as e:
        logger.error(f"Bot test failed: {e}")


async def send_test_summary():
    """Send a test summary to all subscribers."""
    logger.info("Sending test summary to subscribers...")
    
    from src.telegram_bot.bot import bot
    from src.llm_module.summarizer import NewsSummarizer
    from src.models.schemas import Summary
    from datetime import datetime
    
    try:
        # Create a test summary
        test_summary = Summary(
            date=datetime.now().date(),
            summary_text="This is a test summary to verify the bot is working correctly.",
            news_count=5,
            key_topics=["test", "verification", "bot"]
        )
        
        # Start bot
        await bot.start_bot()
        
        # Send test summary
        await bot.send_summary_to_subscribers(test_summary)
        
        # Stop bot
        await bot.stop_bot()
        
        logger.info("Test summary sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send test summary: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="MarketTwits Summarizer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Dump news command
    dump_parser = subparsers.add_parser("dump", help="Dump news from Telegram")
    dump_parser.add_argument(
        "--days-ago", 
        type=int, 
        default=1, 
        help="Number of days ago to start dumping from"
    )
    
    # Create summary command
    summary_parser = subparsers.add_parser("summary", help="Create summary")
    summary_parser.add_argument(
        "--date", 
        type=str, 
        help="Date to create summary for (YYYY-MM-DD format)"
    )
    
    # Run daily job commands
    subparsers.add_parser("daily-job", help="Run both daily jobs manually")
    subparsers.add_parser("dump-job", help="Run dump job manually")
    subparsers.add_parser("push-job", help="Run push job manually")
    
    # Show news stats command
    subparsers.add_parser("stats", help="Show news statistics")
    
    # Test bot command
    subparsers.add_parser("test-bot", help="Test Telegram bot functionality")
    
    # Send test summary command
    subparsers.add_parser("send-test", help="Send test summary to subscribers")
    
    # Clear latest summary command
    subparsers.add_parser("clear-summary", help="Clear latest summary from Redis")
    
    # Clear summary by date command
    clear_date_parser = subparsers.add_parser("clear-date", help="Clear summary for specific date")
    clear_date_parser.add_argument(
        "--date", 
        type=str, 
        required=True,
        help="Date to clear summary for (YYYY-MM-DD format)"
    )
    
    # Preview news command
    preview_news_parser = subparsers.add_parser("preview-news", help="Preview news items for summarization")
    preview_news_parser.add_argument(
        "--days-ago", 
        type=int, 
        default=1,
        help="Number of days ago to preview (default: 1)"
    )
    preview_news_parser.add_argument(
        "--limit", 
        type=int, 
        default=10,
        help="Number of items to preview (default: 10)"
    )
    
    # Preview summarization command
    preview_sum_parser = subparsers.add_parser("preview-summarization", help="Preview what would be sent to AI")
    preview_sum_parser.add_argument(
        "--days-ago", 
        type=int, 
        default=1,
        help="Number of days ago to preview (default: 1)"
    )
    
    # Clear news data command
    subparsers.add_parser("clear-news", help="Clear all news data from storage")
    
    # Generate fresh summary command
    generate_parser = subparsers.add_parser("generate", help="Generate fresh summary without caching")
    generate_parser.add_argument(
        "--days-ago", 
        type=int, 
        default=1,
        help="Number of days ago to generate summary for (default: 1)"
    )
    
    args = parser.parse_args()
    
    if args.command == "dump":
        asyncio.run(dump_news(args.days_ago))
    elif args.command == "summary":
        asyncio.run(create_summary(args.date))
    elif args.command == "daily-job":
        asyncio.run(run_daily_job())
    elif args.command == "dump-job":
        asyncio.run(run_dump_job())
    elif args.command == "push-job":
        asyncio.run(run_push_job())
    elif args.command == "stats":
        asyncio.run(show_news_stats())
    elif args.command == "test-bot":
        asyncio.run(test_bot())
    elif args.command == "send-test":
        asyncio.run(send_test_summary())
    elif args.command == "clear-summary":
        asyncio.run(clear_latest_summary())
    elif args.command == "clear-date":
        asyncio.run(clear_summary_by_date(args.date))
    elif args.command == "preview-news":
        asyncio.run(preview_news(args.days_ago, args.limit))
    elif args.command == "preview-summarization":
        asyncio.run(preview_summarization(args.days_ago))
    elif args.command == "clear-news":
        asyncio.run(clear_news_data())
    elif args.command == "generate":
        asyncio.run(generate_fresh_summary(args.days_ago))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
