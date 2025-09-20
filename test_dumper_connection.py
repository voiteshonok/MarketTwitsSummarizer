#!/usr/bin/env python3
"""Test dumper connection management."""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dumper.telegram_dumper import TelegramDumper
from src.utils.logger import logger


async def test_connection_management():
    """Test the dumper connection management."""
    print("🔌 Testing Telegram dumper connection management...")
    
    # Set up environment for testing
    os.environ['TELEGRAM_API_ID'] = 'test_api_id'
    os.environ['TELEGRAM_API_HASH'] = 'test_api_hash'
    os.environ['TELEGRAM_CHANNEL_USERNAME'] = 'MarketTwits'
    os.environ['TELEGRAM_SESSION_NAME'] = 'test_session'
    
    dumper = TelegramDumper()
    
    print(f"Initial connection state: {dumper.is_connected()}")
    
    # Test connection
    print("🔄 Testing connection...")
    try:
        result = await dumper.connect()
        print(f"Connection result: {result}")
        print(f"Connection state after connect: {dumper.is_connected()}")
        
        # Test duplicate connection (should be fast)
        print("🔄 Testing duplicate connection (should be fast)...")
        start_time = asyncio.get_event_loop().time()
        result2 = await dumper.connect()
        end_time = asyncio.get_event_loop().time()
        
        print(f"Duplicate connection result: {result2}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"Connection state after duplicate: {dumper.is_connected()}")
        
        # Test ensure_connected
        print("🔄 Testing ensure_connected...")
        result3 = await dumper.ensure_connected()
        print(f"Ensure connected result: {result3}")
        print(f"Connection state after ensure: {dumper.is_connected()}")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
    
    # Test disconnection
    print("🔄 Testing disconnection...")
    try:
        await dumper.disconnect()
        print(f"Connection state after disconnect: {dumper.is_connected()}")
        
        # Test duplicate disconnection
        await dumper.disconnect()
        print(f"Connection state after duplicate disconnect: {dumper.is_connected()}")
        
    except Exception as e:
        print(f"❌ Disconnection test failed: {e}")
    
    # Test close
    print("🔄 Testing close...")
    try:
        await dumper.close()
        print(f"Connection state after close: {dumper.is_connected()}")
    except Exception as e:
        print(f"❌ Close test failed: {e}")
    
    print("✅ Connection management test completed!")


if __name__ == "__main__":
    asyncio.run(test_connection_management())
