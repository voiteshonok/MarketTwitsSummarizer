#!/usr/bin/env python3
"""Check and fix webhook issues."""

import asyncio
import os
from telegram import Bot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual token


async def check_and_fix_webhook():
    """Check webhook status and fix if needed."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your bot token in the BOT_TOKEN variable!")
        return
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Get bot info
        print("🤖 Getting bot info...")
        info = await bot.get_me()
        print(f"✅ Bot: {info.first_name} (@{info.username})")
        
        # Check webhook
        print("\n🔍 Checking webhook status...")
        webhook = await bot.get_webhook_info()
        print(f"Webhook URL: {webhook.url}")
        print(f"Pending updates: {webhook.pending_update_count}")
        
        if webhook.url:
            print("⚠️  Webhook is set - this blocks polling!")
            print("🔧 Deleting webhook...")
            await bot.delete_webhook()
            print("✅ Webhook deleted successfully")
        else:
            print("✅ No webhook set - polling should work")
        
        print("\n🎯 Bot is ready for polling!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "Unauthorized" in str(e):
            print("🔑 Bot token is incorrect!")
        elif "Network" in str(e):
            print("🌐 Network connection issue!")


if __name__ == "__main__":
    asyncio.run(check_and_fix_webhook())
