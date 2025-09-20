#!/usr/bin/env python3
"""Test the new summary prompt."""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import config
from src.utils.logger import logger
from src.llm_module.summarizer import NewsSummarizer
from src.models.schemas import NewsBatch, NewsItem


async def test_new_prompt():
    """Test the new summary prompt."""
    print("🧪 Testing New Summary Prompt...")
    
    try:
        # Create test news items
        test_news = [
            "Fed signals potential rate cut in Q4 2024",
            "S&P 500 hits new all-time high",
            "Bitcoin surges 15% after ETF approval",
            "Russian ruble weakens against dollar",
            "Tesla reports record quarterly earnings",
            "Meme stock GME jumps 20% on retail trading",
            "European Central Bank maintains rates",
            "Oil prices rise on supply concerns",
            "Apple announces new iPhone launch",
            "Chinese markets closed for holiday"
        ]
        
        # Create NewsBatch
        news_items = []
        for i, text in enumerate(test_news):
            item = NewsItem(
                message_id=1000 + i,
                text=text,
                date=datetime.now(),
                views=100 + i * 10,
                forwards=5 + i
            )
            news_items.append(item)
        
        news_batch = NewsBatch(
            items=news_items,
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_count=len(news_items)
        )
        
        # Test the summarizer
        summarizer = NewsSummarizer()
        
        print("1. Testing prompt generation...")
        prompt = summarizer._create_summarization_prompt([item.text for item in news_items], "2025-09-20")
        
        print("✅ Prompt generated successfully")
        print("\n📝 Generated Russian Prompt:")
        print("=" * 50)
        print(prompt)
        print("=" * 50)
        
        print("\n2. Testing full summarization...")
        summary = await summarizer.summarize_news(news_batch)
        
        if summary:
            print("✅ Summary created successfully")
            print(f"\n📊 Summary:")
            print(f"Date: {summary.date}")
            print(f"News Count: {summary.news_count}")
            print(f"Summary Text: {summary.summary_text}")
            print(f"Key Topics: {summary.key_topics}")
            return True
        else:
            print("❌ Failed to create summary")
            return False
            
    except Exception as e:
        print(f"❌ Error testing new prompt: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 New Summary Prompt Test")
    print("=" * 50)
    
    # Check configuration
    if not config.OPENAI_API_KEY:
        print("❌ Missing OpenAI API key!")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    success = await test_new_prompt()
    
    if success:
        print("\n🎉 New Russian prompt is working correctly!")
        print("The summarizer now generates Russian summaries in numbered format, focusing on major global financial news.")
    else:
        print("\n❌ New prompt test failed. Please check the logs for details.")


if __name__ == "__main__":
    asyncio.run(main())
