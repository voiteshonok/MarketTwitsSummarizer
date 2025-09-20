"""Example usage of the MarketTwits Summarizer system."""

import asyncio
from datetime import datetime, timedelta

from src.dumper.telegram_dumper import TelegramDumper
from src.llm_module.summarizer import NewsSummarizer
from src.utils.logger import logger


async def example_workflow():
    """Example of how to use the system components."""
    
    logger.info("Starting MarketTwits Summarizer example workflow")
    
    # Initialize components
    dumper = TelegramDumper()
    summarizer = NewsSummarizer()
    
    # Step 1: Dump news from Telegram
    logger.info("Step 1: Dumping news from Telegram channel")
    from_date = datetime.now() - timedelta(days=1)
    dump_success = await dumper.dump_news(from_date)
    
    if not dump_success:
        logger.error("Failed to dump news")
        return
    
    # Step 2: Get the news batch
    logger.info("Step 2: Retrieving news batch")
    news_batch = dumper.get_news_for_date(from_date)
    
    if not news_batch:
        logger.error("No news batch found")
        return
    
    logger.info(f"Found {len(news_batch.items)} news items")
    
    # Step 3: Create summary
    logger.info("Step 3: Creating AI summary")
    summary = await summarizer.process_news_batch(news_batch)
    
    if not summary:
        logger.error("Failed to create summary")
        return
    
    # Step 4: Display results
    logger.info("Step 4: Displaying results")
    print("\n" + "="*50)
    print("DAILY MARKET SUMMARY")
    print("="*50)
    print(f"Date: {summary.date}")
    print(f"News Count: {summary.news_count}")
    print(f"Key Topics: {', '.join(summary.key_topics)}")
    print("\nSummary:")
    print(summary.summary_text)
    print("="*50)
    
    # Step 5: Save to cache
    logger.info("Step 5: Summary saved to cache")
    
    logger.info("Example workflow completed successfully")


async def example_api_usage():
    """Example of API usage."""
    import httpx
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        
        # Subscribe a user
        subscription_data = {
            "user_id": 12345,
            "username": "example_user"
        }
        response = await client.post(f"{base_url}/subscribe", json=subscription_data)
        print(f"Subscription: {response.status_code}")
        
        # Get latest summary
        response = await client.get(f"{base_url}/summary/latest")
        if response.status_code == 200:
            data = response.json()
            print(f"Latest summary: {data['summary']['summary_text']}")
        else:
            print(f"Failed to get summary: {response.status_code}")


if __name__ == "__main__":
    print("MarketTwits Summarizer - Example Usage")
    print("Choose an example to run:")
    print("1. Workflow example (dumper + summarizer)")
    print("2. API usage example")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(example_workflow())
    elif choice == "2":
        asyncio.run(example_api_usage())
    else:
        print("Invalid choice")
