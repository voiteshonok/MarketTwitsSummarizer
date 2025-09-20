#!/usr/bin/env python3
"""Test the Redis-based approach for storing and retrieving summaries."""

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


async def test_redis_storage():
    """Test storing and retrieving summaries from Redis."""
    print("🧪 Testing Redis Storage...")
    
    try:
        # Create a test summary
        test_summary = Summary(
            title="Test Daily Summary",
            content="This is a test summary for testing Redis storage functionality.",
            date=datetime.now(),
            news_count=10,
            key_points=["Test Point 1", "Test Point 2", "Test Point 3"]
        )
        
        # Store in Redis
        print("1. Storing test summary in Redis...")
        date_str = test_summary.date.strftime('%Y%m%d')
        redis_key = f"summary:{date_str}"
        redis_client.set(redis_key, test_summary.dict())
        redis_client.set("latest_summary", test_summary.dict())
        
        print("✅ Test summary stored successfully")
        
        # Retrieve from Redis
        print("2. Retrieving summary from Redis...")
        retrieved_data = redis_client.get("latest_summary")
        
        if retrieved_data:
            retrieved_summary = Summary(**retrieved_data)
            print("✅ Summary retrieved successfully")
            print(f"   Title: {retrieved_summary.title}")
            print(f"   Content: {retrieved_summary.content[:50]}...")
            print(f"   Date: {retrieved_summary.date}")
            print(f"   News Count: {retrieved_summary.news_count}")
            print(f"   Key Points: {retrieved_summary.key_points}")
            return True
        else:
            print("❌ Failed to retrieve summary from Redis")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Redis storage: {e}")
        return False


async def test_standalone_dumper():
    """Test the standalone dumper process."""
    print("\n🧪 Testing Standalone Dumper...")
    
    try:
        import subprocess
        
        # Run standalone dumper
        print("1. Running standalone dumper...")
        result = subprocess.run([
            sys.executable, "standalone_dumper.py", "--days-ago", "1"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Standalone dumper completed successfully")
            print(f"   Output: {result.stdout}")
            
            # Check if summary was stored in Redis
            print("2. Checking if summary was stored in Redis...")
            summary_data = redis_client.get("latest_summary")
            
            if summary_data:
                summary = Summary(**summary_data)
                print("✅ Summary found in Redis")
                print(f"   Title: {summary.title}")
                print(f"   News Count: {summary.news_count}")
                return True
            else:
                print("❌ No summary found in Redis")
                return False
        else:
            print(f"❌ Standalone dumper failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Standalone dumper timed out")
        return False
    except Exception as e:
        print(f"❌ Error running standalone dumper: {e}")
        return False


def test_server_endpoints():
    """Test server endpoints that read from Redis."""
    print("\n🧪 Testing Server Endpoints...")
    
    try:
        import requests
        
        # Test latest summary endpoint
        print("1. Testing /summary/latest endpoint...")
        response = requests.get(
            f"http://{config.HOST}:{config.PORT}/summary/latest",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Latest summary endpoint works")
                print(f"   Title: {data['summary']['title']}")
                return True
            else:
                print(f"ℹ️  No summary available: {data.get('message')}")
                return True
        else:
            print(f"❌ Latest summary endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing server endpoints: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Redis-Based Architecture Test")
    print("=" * 50)
    
    # Check configuration
    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
        print("❌ Missing API credentials!")
        print("Please set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env file")
        return
    
    # Run tests
    tests = [
        ("Redis Storage", test_redis_storage),
        ("Standalone Dumper", test_standalone_dumper),
        ("Server Endpoints", test_server_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
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
        print("🎉 All tests passed! The Redis-based architecture is working correctly.")
    else:
        print("❌ Some tests failed. Please check the logs for details.")


if __name__ == "__main__":
    asyncio.run(main())
