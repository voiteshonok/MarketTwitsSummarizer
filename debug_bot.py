"""Debug script for Telegram bot."""

import asyncio
import os
from telegram import Bot
from telegram.error import TelegramError

# Set up environment for testing
os.environ['TELEGRAM_BOT_TOKEN'] = 'your_bot_token_here'  # Replace with your actual token

from src.utils.config import config
from src.utils.logger import logger


async def test_bot_connection():
    """Test basic bot connection and functionality."""
    try:
        logger.info("Testing bot connection...")
        
        # Create bot instance
        bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        
        # Test bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot info: {bot_info}")
        
        # Test webhook info
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info}")
        
        # If webhook is set, delete it to use polling
        if webhook_info.url:
            logger.info("Webhook is set, deleting it to use polling...")
            await bot.delete_webhook()
            logger.info("Webhook deleted successfully")
        
        # Test sending a message to yourself (replace with your user ID)
        # user_id = 123456789  # Replace with your Telegram user ID
        # await bot.send_message(chat_id=user_id, text="Test message from bot")
        # logger.info("Test message sent successfully")
        
        logger.info("Bot connection test completed successfully!")
        
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
    except Exception as e:
        logger.error(f"Error testing bot: {e}")


async def test_bot_with_polling():
    """Test bot with polling."""
    try:
        from src.telegram_bot.bot import bot
        
        logger.info("Testing bot with polling...")
        
        # Start bot
        await bot.start_bot()
        logger.info("Bot started, waiting for messages...")
        
        # Wait for 30 seconds to receive messages
        await asyncio.sleep(30)
        
        # Stop bot
        await bot.stop_bot()
        logger.info("Bot test completed")
        
    except Exception as e:
        logger.error(f"Error testing bot with polling: {e}")


if __name__ == "__main__":
    print("Telegram Bot Debug Tool")
    print("1. Test bot connection")
    print("2. Test bot with polling")
    
    choice = input("Choose test (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_bot_connection())
    elif choice == "2":
        asyncio.run(test_bot_with_polling())
    else:
        print("Invalid choice")
