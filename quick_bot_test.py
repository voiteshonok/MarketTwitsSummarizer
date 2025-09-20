#!/usr/bin/env python3
"""Quick bot test with the new Bot implementation."""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from telegram import Bot, Update


async def handle_update(bot: Bot, update: Update):
    """Handle incoming updates."""
    if update.message:
        user = update.message.from_user
        text = update.message.text
        
        print(f"📨 Received message from {user.first_name} ({user.id}): {text}")
        
        if text == '/start':
            await update.message.reply_text(
                f"🎉 Hello {user.first_name}! I received your /start command.\n\n"
                "This is a test of the new Bot implementation."
            )
        else:
            await update.message.reply_text(f"🔄 Echo: {text}")


async def poll_updates(bot: Bot):
    """Poll for updates."""
    last_update_id = 0
    
    print("🔄 Starting to poll for updates...")
    
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
            print(f"❌ Error polling updates: {e}")
            await asyncio.sleep(5)


async def main():
    """Main function."""
    # Get bot token from environment or prompt
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ No bot token found!")
        print("Set TELEGRAM_BOT_TOKEN environment variable or edit this script")
        print("Example: export TELEGRAM_BOT_TOKEN='your_token_here'")
        return
    
    print("🤖 Starting quick bot test...")
    print(f"Bot token: {bot_token[:10]}...")
    
    try:
        # Create bot
        bot = Bot(token=bot_token)
        
        # Test connection
        print("🔌 Testing bot connection...")
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: {bot_info.first_name} (@{bot_info.username})")
        
        # Check webhook
        print("🔍 Checking webhook status...")
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            print("⚠️  Webhook detected, deleting it...")
            await bot.delete_webhook()
            print("✅ Webhook deleted")
        else:
            print("✅ No webhook set")
        
        print("\n" + "="*50)
        print("✅ Bot is ready! Send messages to your bot now.")
        print("📱 Try sending /start or any message")
        print("⏹️  Press Ctrl+C to stop")
        print("="*50)
        
        # Start polling
        await poll_updates(bot)
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping bot...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("1. Check if your bot token is correct")
        print("2. Make sure you're messaging the bot in a private chat")
        print("3. Check if there's a webhook set")
    finally:
        print("✅ Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
