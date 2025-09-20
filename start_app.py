#!/usr/bin/env python3
"""Startup script that ensures Telegram sessions are ready before starting the app."""

import subprocess
import sys
import os

def check_sessions():
    """Check if all Telegram session files exist."""
    print("🔍 Checking Telegram sessions...")
    
    result = subprocess.run([
        sys.executable, "simple_session_check.py"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All sessions are ready!")
        return True
    else:
        print("❌ Some session files are missing!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

def start_application():
    """Start the main application."""
    print("🚀 Starting MarketTwits Summarizer application...")
    
    # Start the main application
    subprocess.run([sys.executable, "main.py"])

def main():
    """Main startup function."""
    print("=" * 60)
    print("🎯 MarketTwits Summarizer Startup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if required environment variables are set
    required_vars = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or environment configuration.")
        sys.exit(1)
    
    # Check Telegram sessions
    if not check_sessions():
        print("\n⚠️  Some Telegram sessions are not ready.")
        print("Please run the setup manually:")
        print("   python setup_telegram_sessions.py")
        print("\nOr copy your authorized session files to the container.")
        sys.exit(1)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
