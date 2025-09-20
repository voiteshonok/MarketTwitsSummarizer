#!/usr/bin/env python3
"""Debug script to check timezone settings and scheduler times."""

import os
import sys
from datetime import datetime
import pytz

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import config

def debug_timezone():
    """Debug timezone settings and scheduler times."""
    print("=== Timezone Debug Information ===")
    print()
    
    # Current system time
    print("1. System Information:")
    print(f"   Current UTC time: {datetime.utcnow()}")
    print(f"   Current local time: {datetime.now()}")
    print(f"   System timezone: {datetime.now().astimezone().tzinfo}")
    print()
    
    # Configuration
    print("2. Configuration:")
    print(f"   SCHEDULER_TIMEZONE: {config.SCHEDULER_TIMEZONE}")
    print()
    
    # Timezone object
    try:
        tz = pytz.timezone(config.SCHEDULER_TIMEZONE)
        print("3. Timezone Details:")
        print(f"   Timezone object: {tz}")
        print(f"   UTC offset: {tz.utcoffset(datetime.now())}")
        print(f"   Current time in {config.SCHEDULER_TIMEZONE}: {datetime.now(tz)}")
        print()
        
        # Next scheduled times
        print("4. Next Scheduled Times:")
        now = datetime.now(tz)
        
        # News dump job (15:00)
        dump_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        if dump_time <= now:
            dump_time = dump_time.replace(day=dump_time.day + 1)
        
        # Summary push job (15:07)
        push_time = now.replace(hour=15, minute=7, second=0, microsecond=0)
        if push_time <= now:
            push_time = push_time.replace(day=push_time.day + 1)
        
        print(f"   Next news dump: {dump_time} ({config.SCHEDULER_TIMEZONE})")
        print(f"   Next summary push: {push_time} ({config.SCHEDULER_TIMEZONE})")
        print()
        
        # Convert to UTC for reference
        print("5. UTC Times (for reference):")
        print(f"   News dump UTC: {dump_time.astimezone(pytz.UTC)}")
        print(f"   Summary push UTC: {push_time.astimezone(pytz.UTC)}")
        print()
        
        # Time until next job
        time_until_dump = dump_time - now
        time_until_push = push_time - now
        
        print("6. Time Until Next Jobs:")
        print(f"   Until news dump: {time_until_dump}")
        print(f"   Until summary push: {time_until_push}")
        
    except Exception as e:
        print(f"❌ Error with timezone {config.SCHEDULER_TIMEZONE}: {e}")
        print("Available timezones:")
        for tz in pytz.all_timezones:
            if 'Moscow' in tz or 'Europe' in tz:
                print(f"   {tz}")

if __name__ == "__main__":
    debug_timezone()
