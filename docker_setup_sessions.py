#!/usr/bin/env python3
"""Docker-specific script for setting up Telegram sessions."""

import asyncio
import os
import sys
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def setup_session_interactive(session_name: str) -> bool:
    """Set up a Telegram session with interactive prompts."""
    print(f"\n🔧 Setting up session: {session_name}")
    
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    if not api_id or not api_hash:
        print(f"❌ Missing TELEGRAM_API_ID or TELEGRAM_API_HASH in environment")
        return False
    
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        print(f"📱 Starting Telegram client for {session_name}...")
        print("   You will be prompted to enter your phone number and verification code.")
        
        await client.start()
        
        # Get user info to confirm authorization
        me = await client.get_me()
        print(f"✅ Session {session_name} authorized for: {me.first_name} (@{me.username})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to set up session {session_name}: {e}")
        return False
    finally:
        await client.disconnect()

async def main():
    """Main function to set up all required sessions."""
    print("=" * 60)
    print("🚀 Telegram Sessions Setup for Docker")
    print("=" * 60)
    
    # Sessions required by the application
    sessions = [
        "market_twits_bot",
        "market_twits_dumper", 
        "market_twits_api"
    ]
    
    print(f"📋 Setting up {len(sessions)} Telegram sessions...")
    print("   This process will require you to:")
    print("   1. Enter your phone number")
    print("   2. Enter the verification code from Telegram")
    print("   3. Repeat for each session")
    print()
    
    success_count = 0
    
    for i, session in enumerate(sessions, 1):
        print(f"\n[{i}/{len(sessions)}] Setting up {session}...")
        
        if await setup_session_interactive(session):
            success_count += 1
            print(f"✅ {session} completed successfully")
        else:
            print(f"❌ {session} failed")
    
    print("\n" + "=" * 60)
    print("📊 Setup Summary")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{len(sessions)}")
    
    if success_count == len(sessions):
        print("🎉 All sessions are ready!")
        print("   You can now run: docker-compose up -d")
        return True
    else:
        print("⚠️  Some sessions failed.")
        print("   You may need to run this script again or copy session files manually.")
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
