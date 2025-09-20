#!/usr/bin/env python3
"""Simple bot test using direct Bot class."""

import asyncio
import os
from telegram import Bot, Update

# Set your bot token here
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual token


async def handle_update(bot: Bot, update: Update):
    """Handle incoming updates."""
    if update.message:
        user = update.message.from_user
        text = update.message.text
        
        print(f"Received message from {user.first_name} ({user.id}): {text}")
        
        if text == '/start':
            await update.message.reply_text(f"Hello {user.first_name}! I received your /start command.")
        else:
            await update.message.reply_text(f"Echo: {text}")


async def poll_updates(bot: Bot):
    """Poll for updates."""
    last_update_id = 0
    
    while True:
        try:
            # Get updates
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=10)
            
            for update in updates:
                last_update_id = update.update_id
                await handle_update(bot, update)
            
            # Small delay
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error polling updates: {e}")
            await asyncio.sleep(5)


async def main():
    """Main function."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your bot token in the BOT_TOKEN variable!")
        print("Edit this file and replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token")
        return
    
    print("🤖 Starting simple bot test...")
    print(f"Bot token: {BOT_TOKEN[:10]}...")
    
    try:
        # Create bot
        bot = Bot(token=BOT_TOKEN)
        
        # Test connection
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: {bot_info.first_name} (@{bot_info.username})")
        
        # Check webhook
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            print("⚠️  Webhook detected, deleting it...")
            await bot.delete_webhook()
            print("✅ Webhook deleted")
        else:
            print("✅ No webhook set")
        
        print("🔄 Starting polling...")
        print("✅ Bot is running! Send messages to your bot.")
        print("📱 Try sending /start or any message to your bot")
        print("⏹️  Press Ctrl+C to stop.")
        
        # Start polling
        await poll_updates(bot)
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping bot...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Check if your bot token is correct")
        print("2. Make sure you're messaging the bot in a private chat")
        print("3. Check if there's a webhook set")
        print("4. Try deleting webhook")
    finally:
        print("✅ Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
