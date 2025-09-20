#!/usr/bin/env python3
"""Test script to verify scheduler times are correct."""

import os
import sys
from datetime import datetime
import pytz

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import config
from apscheduler.triggers.cron import CronTrigger

def test_scheduler_times():
    """Test the actual scheduler times."""
    print("=== Scheduler Time Test ===")
    print()
    
    # Get timezone
    tz = pytz.timezone(config.SCHEDULER_TIMEZONE)
    now = datetime.now(tz)
    
    print(f"Current time in {config.SCHEDULER_TIMEZONE}: {now}")
    print()
    
    # Test news dump trigger (15:00)
    dump_trigger = CronTrigger(hour=15, minute=0, timezone=config.SCHEDULER_TIMEZONE)
    next_dump = dump_trigger.get_next_fire_time(None, now)
    
    # Test summary push trigger (15:07)
    push_trigger = CronTrigger(hour=15, minute=7, timezone=config.SCHEDULER_TIMEZONE)
    next_push = push_trigger.get_next_fire_time(None, now)
    
    print("Next scheduled times:")
    print(f"  News dump: {next_dump}")
    print(f"  Summary push: {next_push}")
    print()
    
    if next_dump:
        time_until_dump = next_dump - now
        print(f"Time until news dump: {time_until_dump}")
    
    if next_push:
        time_until_push = next_push - now
        print(f"Time until summary push: {time_until_push}")
    
    print()
    print("Scheduler configuration:")
    print(f"  Timezone: {config.SCHEDULER_TIMEZONE}")
    print(f"  News dump: 15:00 {config.SCHEDULER_TIMEZONE}")
    print(f"  Summary push: 15:07 {config.SCHEDULER_TIMEZONE}")

if __name__ == "__main__":
    test_scheduler_times()
