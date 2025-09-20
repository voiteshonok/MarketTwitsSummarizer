#!/usr/bin/env python3
"""Simple script to check if Telegram session files exist."""

import os
import sys

def check_sessions():
    """Check if all required session files exist."""
    sessions = [
        "market_twits_bot.session",
        "market_twits_dumper.session", 
        "market_twits_api.session"
    ]
    
    missing_sessions = []
    
    for session in sessions:
        if os.path.exists(session):
            print(f"✅ {session} exists")
        else:
            print(f"❌ {session} missing")
            missing_sessions.append(session)
    
    if missing_sessions:
        print(f"\n⚠️  Missing sessions: {', '.join(missing_sessions)}")
        print("Please copy your authorized session files:")
        print("   docker cp market_twits_parser.session market_twits_app:/app/market_twits_bot.session")
        print("   docker cp market_twits_parser.session market_twits_app:/app/market_twits_dumper.session")
        print("   docker cp market_twits_parser.session market_twits_app:/app/market_twits_api.session")
        return False
    
    print("\n🎉 All session files are present!")
    return True

if __name__ == "__main__":
    try:
        result = check_sessions()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
