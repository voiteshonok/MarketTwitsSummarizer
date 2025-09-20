"""Simple bot test to debug message receiving."""

import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set your bot token here
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual token


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("Hello! I received your /start command.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages."""
    user = update.effective_user
    message_text = update.message.text
    
    print(f"Received message from {user.first_name} ({user.id}): {message_text}")
    
    await update.message.reply_text(f"Echo: {message_text}")


async def main():
    """Main function."""
    print("Starting simple bot test...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    try:
        # Start polling
        print("Starting bot polling...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        print("Bot is running! Send messages to your bot.")
        print("Press Ctrl+C to stop.")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping bot...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("Bot stopped.")


if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please set your bot token in the BOT_TOKEN variable!")
    else:
        asyncio.run(main())
