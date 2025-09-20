#!/usr/bin/env python3
"""Test timezone configuration."""

import os
import sys
from datetime import datetime
import pytz

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import config


def test_timezone():
    """Test timezone configuration."""
    print("🕐 Testing timezone configuration...")
    
    # Get configured timezone
    timezone_name = config.SCHEDULER_TIMEZONE
    print(f"Configured timezone: {timezone_name}")
    
    try:
        # Create timezone object
        tz = pytz.timezone(timezone_name)
        
        # Get current time in the configured timezone
        now_utc = datetime.now(pytz.UTC)
        now_local = now_utc.astimezone(tz)
        
        print(f"Current UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Current {timezone_name} time: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Calculate next 7 AM in the configured timezone
        next_7am = now_local.replace(hour=7, minute=0, second=0, microsecond=0)
        if next_7am <= now_local:
            next_7am = next_7am.replace(day=next_7am.day + 1)
        
        print(f"Next 7 AM ({timezone_name}): {next_7am.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Convert to UTC for scheduler
        next_7am_utc = next_7am.astimezone(pytz.UTC)
        print(f"Next 7 AM (UTC): {next_7am_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Show time difference
        time_diff = now_local.utcoffset().total_seconds() / 3600
        print(f"UTC offset: {time_diff:+.0f} hours")
        
        print("\n✅ Timezone configuration is working correctly!")
        
    except Exception as e:
        print(f"❌ Error with timezone configuration: {e}")
        print("Available timezones:")
        print("- Europe/Moscow (UTC+3)")
        print("- Europe/Istanbul (UTC+3)")
        print("- Asia/Tehran (UTC+3:30)")
        print("- Asia/Dubai (UTC+4)")


if __name__ == "__main__":
    test_timezone()
