#!/usr/bin/env python3
"""Script to generate Telegram SESSION_STRING for use in .env file."""

import os
import sys
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

def generate_session_string():
    """Generate a Telegram session string."""
    print("=== Telegram Session String Generator ===")
    print()
    print("This script will generate a SESSION_STRING that you can use in your .env file")
    print("to avoid SQLite database locking issues.")
    print()
    
    # Get credentials
    api_id = input("Enter your TELEGRAM_API_ID: ").strip()
    api_hash = input("Enter your TELEGRAM_API_HASH: ").strip()
    
    if not api_id or not api_hash:
        print("❌ API ID and API Hash are required")
        return
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ API ID must be a number")
        return
    
    print()
    print("Connecting to Telegram...")
    print("You will be asked to enter your phone number and verification code.")
    print()
    
    try:
        # Create client with StringSession
        with TelegramClient(StringSession(), api_id, api_hash) as client:
            # This will prompt for phone number and code
            client.start()
            
            # Get the session string
            session_string = client.session.save()
            
            print()
            print("=" * 80)
            print("✅ Session string generated successfully!")
            print("=" * 80)
            print()
            print("Add this to your .env file:")
            print()
            print(f"TELEGRAM_SESSION_STRING={session_string}")
            print()
            print("=" * 80)
            print()
            print("Benefits of using SESSION_STRING:")
            print("  ✅ No SQLite database files")
            print("  ✅ No database locking issues")
            print("  ✅ Multiple instances can run simultaneously")
            print("  ✅ Works better in Docker containers")
            print()
            print("Note: Keep this session string secure! It provides access to your Telegram account.")
            
    except Exception as e:
        print(f"❌ Error generating session string: {e}")
        return

if __name__ == "__main__":
    generate_session_string()
