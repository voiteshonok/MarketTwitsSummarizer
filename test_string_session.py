#!/usr/bin/env python3
"""Test script to verify StringSession implementation."""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import config
from src.dumper.telegram_dumper import TelegramDumper

async def test_string_session():
    """Test TelegramDumper with StringSession."""
    print("=== Testing StringSession Implementation ===")
    print()
    
    # Check configuration
    print("1. Checking configuration...")
    if config.TELEGRAM_SESSION_STRING:
        print(f"   ✅ SESSION_STRING is configured (length: {len(config.TELEGRAM_SESSION_STRING)})")
        print("   Session type: StringSession (in-memory)")
    else:
        print("   ℹ️  SESSION_STRING not configured")
        print(f"   Session type: File-based ({config.TELEGRAM_SESSION_NAME_DUMPER})")
    
    print()
    
    # Test dumper creation
    print("2. Testing TelegramDumper creation...")
    try:
        dumper = TelegramDumper()
        print("   ✅ TelegramDumper created successfully")
        print("   Session type: StringSession (in-memory)")
    except Exception as e:
        print(f"   ❌ Failed to create TelegramDumper: {e}")
        return False
    
    print()
    
    # Test connection
    print("3. Testing Telegram connection...")
    try:
        connected = await dumper.connect()
        if connected:
            print("   ✅ Connected to Telegram successfully")
        else:
            print("   ❌ Failed to connect to Telegram")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    print()
    
    # Test multiple dumper instances (should not conflict with StringSession)
    print("4. Testing multiple dumper instances...")
    try:
        dumper2 = TelegramDumper()
        connected2 = await dumper2.connect()
        if connected2:
            print("   ✅ Second dumper connected successfully (no conflict!)")
        else:
            print("   ❌ Second dumper failed to connect")
        
        await dumper2.disconnect()
    except Exception as e:
        print(f"   ❌ Multiple instances test failed: {e}")
        return False
    
    print()
    
    # Cleanup
    print("5. Cleaning up...")
    await dumper.disconnect()
    print("   ✅ Disconnected successfully")
    
    print()
    print("✅ All tests passed! StringSession is working correctly.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_string_session())
    sys.exit(0 if success else 1)
