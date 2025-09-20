#!/usr/bin/env python3
"""Test Redis retrieval of summaries."""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import config
from src.utils.logger import logger
from src.utils.redis_client import redis_client
from src.models.schemas import Summary


async def test_redis_retrieval():
    """Test retrieving summaries from Redis."""
    print("🧪 Testing Redis Summary Retrieval...")
    
    try:
        # Test 1: Check if latest summary exists
        print("1. Checking latest summary in Redis...")
        latest_data = redis_client.get_json("latest_summary")
        
        if latest_data:
            print("✅ Latest summary found in Redis")
            print(f"   Keys: {list(latest_data.keys())}")
            
            # Test creating Summary object
            try:
                summary = Summary(**latest_data)
                print("✅ Successfully created Summary object")
                print(f"   Date: {summary.date}")
                print(f"   Summary text: {summary.summary_text[:100]}...")
                print(f"   News count: {summary.news_count}")
                print(f"   Key topics: {summary.key_topics}")
                return True
            except Exception as e:
                print(f"❌ Failed to create Summary object: {e}")
                return False
        else:
            print("ℹ️  No latest summary found in Redis")
            
            # Test 2: Check if any summaries exist by date
            print("2. Checking summaries by date...")
            today = datetime.now()
            date_str = today.strftime('%Y%m%d')
            redis_key = f"summary:{date_str}"
            
            summary_data = redis_client.get_json(redis_key)
            if summary_data:
                print(f"✅ Found summary for today ({date_str})")
                try:
                    summary = Summary(**summary_data)
                    print(f"   Summary text: {summary.summary_text[:100]}...")
                    return True
                except Exception as e:
                    print(f"❌ Failed to create Summary object: {e}")
                    return False
            else:
                print(f"ℹ️  No summary found for today ({date_str})")
                return False
                
    except Exception as e:
        print(f"❌ Error testing Redis retrieval: {e}")
        return False


async def test_bot_methods():
    """Test bot methods for retrieving summaries."""
    print("\n🧪 Testing Bot Methods...")
    
    try:
        from src.telegram_bot.bot import MarketTwitsBot
        
        bot = MarketTwitsBot()
        
        # Test get_latest_summary_from_redis
        print("1. Testing get_latest_summary_from_redis...")
        summary = bot.get_latest_summary_from_redis()
        
        if summary:
            print("✅ Bot successfully retrieved latest summary")
            print(f"   Date: {summary.date}")
            print(f"   Text: {summary.summary_text[:50]}...")
            return True
        else:
            print("ℹ️  No latest summary available")
            
            # Test get_summary_for_date_from_redis
            print("2. Testing get_summary_for_date_from_redis...")
            today = datetime.now()
            summary = bot.get_summary_for_date_from_redis(today)
            
            if summary:
                print("✅ Bot successfully retrieved summary for today")
                print(f"   Date: {summary.date}")
                print(f"   Text: {summary.summary_text[:50]}...")
                return True
            else:
                print("ℹ️  No summary available for today")
                return False
                
    except Exception as e:
        print(f"❌ Error testing bot methods: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Redis Summary Retrieval Test")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Redis Retrieval", test_redis_retrieval),
        ("Bot Methods", test_bot_methods)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("🎉 All tests passed! Redis retrieval is working correctly.")
    else:
        print("❌ Some tests failed. Please check the logs for details.")


if __name__ == "__main__":
    asyncio.run(main())
