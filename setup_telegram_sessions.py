#!/usr/bin/env python3
"""Script to set up Telegram sessions for the MarketTwits Summarizer."""

import asyncio
import os
import sys
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_session_exists(session_name: str) -> bool:
    """Check if session file exists and is valid."""
    session_file = f"{session_name}.session"
    if not os.path.exists(session_file):
        return False
    
    try:
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        
        if not api_id or not api_hash:
            print(f"❌ Missing TELEGRAM_API_ID or TELEGRAM_API_HASH for {session_name}")
            return False
        
        client = TelegramClient(session_name, api_id, api_hash)
        
        # Try to connect without starting (just check if session is valid)
        try:
            if await client.connect():
                # Check if we're authorized
                if await client.is_user_authorized():
                    await client.disconnect()
                    return True
                await client.disconnect()
        except Exception as e:
            # If database is locked, assume session exists but is being used
            if "database is locked" in str(e):
                print(f"⚠️  Session {session_name} is locked (probably in use)")
                return True
            raise e
        
        return False
    except Exception as e:
        print(f"❌ Error checking session {session_name}: {e}")
        return False

async def setup_session(session_name: str) -> bool:
    """Set up a Telegram session."""
    print(f"🔧 Setting up session: {session_name}")
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print(f"❌ Missing TELEGRAM_API_ID or TELEGRAM_API_HASH")
        return False
    
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        await client.start()
        print(f"✅ Session {session_name} set up successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to set up session {session_name}: {e}")
        return False
    finally:
        await client.disconnect()

async def main():
    """Main function to check and set up all required sessions."""
    print("🚀 Checking Telegram sessions...")
    
    # Sessions required by the application
    sessions = [
        "market_twits_bot",
        "market_twits_dumper", 
        "market_twits_api"
    ]
    
    missing_sessions = []
    
    # Check which sessions are missing or invalid
    for session in sessions:
        if await check_session_exists(session):
            print(f"✅ Session {session} is ready")
        else:
            print(f"❌ Session {session} is missing or invalid")
            missing_sessions.append(session)
    
    if not missing_sessions:
        print("\n🎉 All sessions are ready! Application can start.")
        return True
    
    print(f"\n⚠️  {len(missing_sessions)} sessions need to be set up:")
    for session in missing_sessions:
        print(f"   - {session}")
    
    print("\n🔧 Setting up missing sessions...")
    
    success_count = 0
    for session in missing_sessions:
        if await setup_session(session):
            success_count += 1
    
    print(f"\n📊 Setup complete: {success_count}/{len(missing_sessions)} sessions configured")
    
    if success_count == len(missing_sessions):
        print("✅ All sessions ready! You can now run the application.")
        return True
    else:
        print("❌ Some sessions failed. Check the errors above.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
