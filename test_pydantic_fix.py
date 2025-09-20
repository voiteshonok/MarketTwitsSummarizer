#!/usr/bin/env python3
"""Test the Pydantic V2 fix."""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import config
from src.utils.logger import logger
from src.models.schemas import Summary
from src.utils.redis_client import redis_client


async def test_pydantic_fix():
    """Test that Pydantic V2 model_dump() works correctly."""
    print("🧪 Testing Pydantic V2 Fix...")
    
    try:
        # Create a test summary
        test_summary = Summary(
            title="Test Summary",
            content="This is a test summary for Pydantic V2 compatibility.",
            date=datetime.now(),
            news_count=5,
            key_points=["Point 1", "Point 2"]
        )
        
        print("1. Testing model_dump() method...")
        
        # Test model_dump() method
        summary_dict = test_summary.model_dump()
        
        if isinstance(summary_dict, dict):
            print("✅ model_dump() works correctly")
            print(f"   Keys: {list(summary_dict.keys())}")
        else:
            print("❌ model_dump() failed")
            return False
        
        print("2. Testing Redis storage with model_dump()...")
        
        # Test storing in Redis
        redis_key = "test_summary"
        redis_client.set(redis_key, summary_dict)
        
        # Test retrieving from Redis
        retrieved_data = redis_client.get(redis_key)
        
        if retrieved_data and isinstance(retrieved_data, dict):
            print("✅ Redis storage with model_dump() works")
            
            # Test creating Summary from retrieved data
            retrieved_summary = Summary(**retrieved_data)
            print(f"   Retrieved title: {retrieved_summary.title}")
            print(f"   Retrieved content: {retrieved_summary.content[:50]}...")
            
            # Clean up
            redis_client.delete(redis_key)
            print("✅ Cleanup completed")
            
            return True
        else:
            print("❌ Redis storage/retrieval failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Pydantic fix: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Pydantic V2 Compatibility Test")
    print("=" * 50)
    
    success = await test_pydantic_fix()
    
    if success:
        print("\n🎉 Pydantic V2 fix is working correctly!")
        print("The standalone dumper should now work without deprecation warnings.")
    else:
        print("\n❌ Pydantic V2 fix failed. Please check the error messages.")


if __name__ == "__main__":
    asyncio.run(main())
