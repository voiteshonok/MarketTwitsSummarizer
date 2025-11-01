"""Telegram bot for user interaction and notifications."""

import asyncio
import json
import httpx
from datetime import datetime, timedelta
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

from ..utils.config import config
from ..utils.logger import logger
from ..utils.redis_client import redis_client
from ..llm_module.summarizer import NewsSummarizer
from ..dumper.telegram_dumper import TelegramDumper
from ..models.schemas import Summary
import re


class MarketTwitsBot:
    """Telegram bot for MarketTwits summarizer."""
    
    def __init__(self):
        """Initialize the bot."""
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.summarizer = NewsSummarizer()
        self.dumper = TelegramDumper()
        self.running = False
        self._last_update_id = 0
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape special characters for Markdown parsing."""
        # Characters that need to be escaped in Telegram Markdown
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in text)
    
    def get_latest_summary_from_redis(self):
        """Get latest summary from Redis."""
        try:
            summary_data = redis_client.get_json("latest_summary")
            if summary_data:
                return Summary(**summary_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get latest summary from Redis: {e}")
            return None
    
    def get_summary_for_date_from_redis(self, target_date: datetime):
        """Get summary for specific date from Redis."""
        try:
            date_str = target_date.strftime('%Y%m%d')
            redis_key = f"summary:{date_str}"
            summary_data = redis_client.get_json(redis_key)
            if summary_data:
                return Summary(**summary_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get summary for {target_date} from Redis: {e}")
            return None
    
    async def _handle_update(self, update: Update):
        """Handle incoming updates."""
        try:
            if update.message:
                await self._handle_message(update)
            elif update.callback_query:
                await self._handle_callback_query(update)
        except Exception as e:
            logger.error(f"Error handling update: {e}")
    
    async def _handle_message(self, update: Update):
        """Handle text messages."""
        message = update.message
        user = message.from_user
        text = message.text
        
        logger.info(f"Received message from {user.first_name} ({user.id}): {text}")
        
        if text.startswith('/'):
            await self._handle_command(update)
        else:
            await self._handle_text_message(update)
    
    async def _handle_command(self, update: Update):
        """Handle command messages."""
        message = update.message
        text = message.text.lower()
        
        if text == '/start':
            await self.start_command(update)
        elif text == '/help':
            await self.help_command(update)
        elif text == '/subscribe':
            await self.subscribe_command(update)
        elif text == '/unsubscribe':
            await self.unsubscribe_command(update)
        elif text == '/summary':
            await self.summary_command(update)
        elif text == '/latest':
            await self.latest_summary_command(update)
        elif text == '/generate':
            await self.generate_summary_command(update)
        elif text == '/stats':
            await self.stats_command(update)
        else:
            await message.reply_text("Unknown command. Use /help to see available commands.")
    
    async def _handle_text_message(self, update: Update):
        """Handle non-command text messages."""
        message = update.message
        text = message.text.lower()
        
        if any(word in text for word in ['summary', 'news', 'market']):
            await self.summary_command(update)
        elif any(word in text for word in ['subscribe', 'join']):
            await self.subscribe_command(update)
        elif any(word in text for word in ['unsubscribe', 'leave', 'stop']):
            await self.unsubscribe_command(update)
        elif any(word in text for word in ['help', 'commands']):
            await self.help_command(update)
        else:
            await message.reply_text(
                "🤔 I didn't understand that. Use /help to see available commands!"
            )
    
    async def _handle_callback_query(self, update: Update):
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "latest_summary":
            await self._handle_callback_summary(query)
        elif query.data == "stats":
            await self._handle_callback_stats(query)
        elif query.data == "help":
            await self._handle_callback_help(query)
    
    async def _handle_callback_summary(self, query):
        """Handle summary callback query."""
        try:
            if query.data == "latest_summary":
                summary = self.get_latest_summary_from_redis()
            else:
                # For summarization, we want news from the previous day by default
                yesterday = datetime.now() - timedelta(days=1)
                summary = self.get_summary_for_date_from_redis(yesterday)
                if not summary:
                    summary = self.get_latest_summary_from_redis()
            
            if not summary:
                await query.edit_message_text(
                    "📭 No summary available yet.\n\n"
                    "Check back later or use /latest to get the most recent summary."
                )
                return
            
            # Format summary message
            message = f"📈 <b>Daily Market Summary - {summary.date.strftime('%Y-%m-%d')}</b>\n\n"
            message += f"{summary.summary_text}\n\n"
            
            if summary.key_topics:
                key_topics = '\n'.join(summary.key_topics)
                message += f"🔑 <b>Key Topics:</b>\n{key_topics}\n\n"
            
            message += f"📊 Based on {summary.news_count} news items"
            
            await query.edit_message_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error handling callback summary: {e}")
            await query.edit_message_text(
                "❌ Sorry, I couldn't fetch the summary right now. Please try again later."
            )
    
    async def _handle_callback_stats(self, query):
        """Handle stats callback query."""
        try:
            total_news = self.dumper.get_news_count()
            all_news = self.dumper.get_all_news()
            
            # Get recent news count (last 7 days)
            from datetime import timedelta
            week_ago = datetime.now() - timedelta(days=7)
            recent_news = [item for item in all_news if item.date >= week_ago]
            
            # Get subscriber count
            subscribers = redis_client.get_set_members("subscribers")
            
            stats_message = f"""
📊 <b>MarketTwits Statistics</b>

📰 <b>News Data:</b>
• Total news items: {total_news:,}
• Last 7 days: {len(recent_news):,}
• Last updated: {all_news[-1].date.strftime('%Y-%m-%d %H:%M') if all_news else 'Never'}

👥 <b>Subscribers:</b> {len(subscribers):,}

🤖 <b>Bot Status:</b> ✅ Active
            """
            
            await query.edit_message_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error handling callback stats: {e}")
            await query.edit_message_text("❌ Couldn't fetch statistics right now.")
    
    async def _handle_callback_help(self, query):
        """Handle help callback query."""
        help_text = """
🤖 <b>MarketTwits Summarizer Bot</b>

<b>Available Commands:</b>
• `/start` - Start using the bot and subscribe
• `/help` - Show this help message
• `/subscribe` - Subscribe to daily summaries
• `/unsubscribe` - Unsubscribe from summaries
• `/summary` - Get yesterday's summary
• `/latest` - Get the latest available summary
• `/generate` - Generate fresh summary for yesterday (real-time)
• `/stats` - Show news statistics

<b>What I do:</b>
📰 I fetch financial news from @MarketTwits channel
🤖 I use AI to create concise daily summaries
⏰ I send summaries every day at 7 AM (UTC+3)
📊 I provide key market insights and trends

<b>Need help?</b> Just send me a message!
        """
        
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    async def start_command(self, update: Update):
        """Handle /start command."""
        user = update.effective_user
        user_id = user.id
        username = user.username
        
        # Check if user is already subscribed
        redis_key = f"user:{user_id}"
        existing_user = redis_client.get_json(redis_key)
        
        if existing_user:
            message = f"👋 Welcome back, {user.first_name}!\n\n"
            message += "You're already subscribed to daily market summaries.\n\n"
            message += "Use /help to see available commands."
        else:
            # Subscribe the user
            user_data = {
                "user_id": user_id,
                "username": username,
                "subscribed_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            redis_client.set(redis_key, user_data)
            redis_client.add_to_set("subscribers", str(user_id))
            
            message = f"🎉 Welcome to MarketTwits Summarizer, {user.first_name}!\n\n"
            message += "You've been automatically subscribed to daily market summaries.\n\n"
            message += "I'll send you a concise summary of financial news every day at 7 AM (UTC+3).\n\n"
            message += "Use /help to see all available commands."
        
        keyboard = [
            [InlineKeyboardButton("📊 Get Latest Summary", callback_data="latest_summary")],
            [InlineKeyboardButton("📈 View Stats", callback_data="stats")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        logger.info(f"User {user_id} ({username}) started the bot")
    
    async def help_command(self, update: Update):
        """Handle /help command."""
        help_text = """
🤖 <b>MarketTwits Summarizer Bot</b>

<b>Available Commands:</b>
• `/start` - Start using the bot and subscribe
• `/help` - Show this help message
• `/subscribe` - Subscribe to daily summaries
• `/unsubscribe` - Unsubscribe from summaries
• `/summary` - Get yesterday's summary
• `/latest` - Get the latest available summary
• `/generate` - Generate fresh summary for yesterday (real-time)
• `/stats` - Show news statistics

<b>What I do:</b>
📰 I fetch financial news from @MarketTwits channel
🤖 I use AI to create concise daily summaries
⏰ I send summaries every day at 7 AM (UTC+3)
📊 I provide key market insights and trends

<b>Need help?</b> Just send me a message!
        """
        
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def subscribe_command(self, update: Update):
        """Handle /subscribe command."""
        user = update.effective_user
        user_id = user.id
        username = user.username
        
        # Check if already subscribed
        redis_key = f"user:{user_id}"
        existing_user = redis_client.get_json(redis_key)
        
        if existing_user and existing_user.get("is_active", False):
            await update.message.reply_text("✅ You're already subscribed to daily summaries!")
        else:
            # Subscribe the user
            user_data = {
                "user_id": user_id,
                "username": username,
                "subscribed_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            redis_client.set(redis_key, user_data)
            redis_client.add_to_set("subscribers", str(user_id))
            
            await update.message.reply_text(
                "🎉 Successfully subscribed to daily market summaries!\n\n"
                "You'll receive a summary every day at 7 AM (UTC+3)."
            )
            logger.info(f"User {user_id} ({username}) subscribed")
    
    async def unsubscribe_command(self, update: Update):
        """Handle /unsubscribe command."""
        user = update.effective_user
        user_id = user.id
        
        # Unsubscribe the user
        redis_key = f"user:{user_id}"
        redis_client.delete(redis_key)
        redis_client.redis_client.srem("subscribers", str(user_id))
        
        await update.message.reply_text(
            "😢 You've been unsubscribed from daily summaries.\n\n"
            "Use /subscribe to subscribe again anytime!"
        )
        logger.info(f"User {user_id} unsubscribed")
    
    async def summary_command(self, update: Update):
        """Handle /summary command."""
        await self._send_summary(update, "today")
    
    async def latest_summary_command(self, update: Update):
        """Handle /latest command."""
        await self._send_summary(update, "latest")
    
    async def generate_summary_command(self, update: Update):
        """Handle /generate command - create fresh summary without caching."""
        try:
            await update.message.reply_text(
                "🤖 Generating fresh summary for yesterday...\n"
                "This may take a few moments..."
            )
            
            # Generate fresh summary using API
            
            # Use localhost instead of 0.0.0.0 for local connections
            host = "localhost" if config.HOST == "0.0.0.0" else config.HOST
            
            
            # First check if server is ready
            try:
                async with httpx.AsyncClient() as client:
                    health_response = await client.get(
                        f"http://{host}:{config.PORT}/health",
                        timeout=5.0
                    )
                    if health_response.status_code != 200:
                        await update.message.reply_text(
                            "❌ Server is not ready. Please try again in a moment."
                        )
                        return
            except httpx.RequestError:
                await update.message.reply_text(
                    "❌ Server is not available. Please make sure the server is running."
                )
                return
            
            # Now make the actual request with retry logic
            max_retries = 3
            response = None
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"http://{host}:{config.PORT}/news/generate-summary",
                            params={"days_ago": 1},
                            timeout=120.0  # Even longer timeout for AI processing
                        )
                        break  # Success, exit retry loop
                except httpx.TimeoutException:
                    if attempt < max_retries - 1:
                        await update.message.reply_text(
                            f"⏳ Request timed out, retrying... (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    else:
                        raise  # Last attempt failed
                except httpx.RequestError as e:
                    if attempt < max_retries - 1:
                        await update.message.reply_text(
                            f"🔄 Connection error, retrying... (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    else:
                        raise  # Last attempt failed
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    summary_data = data["summary"]
                    summary = Summary(**summary_data)
                    
                    # Format summary message
                    message = f"🆕 <b>Fresh Summary - {summary.date.strftime('%Y-%m-%d')}</b>\n\n"
                    message += f"{summary.summary_text}\n\n"
                    
                    if summary.key_topics:
                        key_topics = '\n'.join(summary.key_topics)
                        message += f"🔑 <b>Key Topics:</b>\n{key_topics}\n\n"
                    
                    message += f"📊 Based on {summary.news_count} news items\n"
                    message += f"⏰ Generated at: {data['generated_at']}"
                    
                    await update.message.reply_text(message, parse_mode='HTML')
                else:
                    await update.message.reply_text(
                        f"❌ Failed to generate summary: {data['message']}"
                    )
            else:
                await update.message.reply_text(
                    f"❌ Server error: {response.status_code}"
                )
                
        except httpx.TimeoutException:
            await update.message.reply_text(
                "❌ Request timed out. The AI processing is taking longer than expected. Please try again later."
            )
        except httpx.ConnectError:
            await update.message.reply_text(
                "❌ Could not connect to server. Make sure the server is running."
            )
        except Exception as e:
            logger.error(f"Error in generate_summary_command: {e}")
            await update.message.reply_text(
                f"❌ Sorry, I couldn't generate the summary right now: {str(e)[:100]}...\n\nPlease try again later."
            )
    
    async def _send_summary(self, update: Update, summary_type: str):
        """Send summary to user."""
        try:
            if summary_type == "today":
                # For summarization, we want news from the previous day by default
                yesterday = datetime.now() - timedelta(days=1)
                summary = self.get_summary_for_date_from_redis(yesterday)
                if not summary:
                    summary = self.get_latest_summary_from_redis()
            else:
                summary = self.get_latest_summary_from_redis()
            
            if not summary:
                await update.message.reply_text(
                    "📭 No summary available yet.\n\n"
                    "Check back later or use /latest to get the most recent summary."
                )
                return
            
            # Format summary message using HTML (more reliable than Markdown)
            message = f"📈 <b>Daily Market Summary - {summary.date.strftime('%Y-%m-%d')}</b>\n\n"
            message += f"{summary.summary_text}\n\n"
            
            if summary.key_topics:
                key_topics = '\n'.join(summary.key_topics)
                message += f"🔑 <b>Key Topics:</b>\n{key_topics}\n\n"
            
            message += f"📊 Based on {summary.news_count} news items"
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error sending summary: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't fetch the summary right now. Please try again later."
            )
    
    async def stats_command(self, update: Update):
        """Handle /stats command."""
        try:
            total_news = self.dumper.get_news_count()
            all_news = self.dumper.get_all_news()
            
            # Get recent news count (last 7 days)
            from datetime import timedelta
            week_ago = datetime.now() - timedelta(days=7)
            recent_news = [item for item in all_news if item.date >= week_ago]
            
            # Get subscriber count
            subscribers = redis_client.get_set_members("subscribers")
            
            stats_message = f"""
📊 <b>MarketTwits Statistics</b>

📰 <b>News Data:</b>
• Total news items: {total_news:,}
• Last 7 days: {len(recent_news):,}
• Last updated: {all_news[-1].date.strftime('%Y-%m-%d %H:%M') if all_news else 'Never'}

👥 <b>Subscribers:</b> {len(subscribers):,}

🤖 <b>Bot Status:</b> ✅ Active
            """
            
            await update.message.reply_text(stats_message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await update.message.reply_text("❌ Couldn't fetch statistics right now.")
    
    async def send_summary_to_subscribers(self, summary):
        """Send summary to all subscribers."""
        try:
            subscribers = redis_client.get_set_members("subscribers")
            
            if not subscribers:
                logger.info("No subscribers to notify")
                return
            
            # Format summary message
            message = f"📈 <b>Daily Market Summary - {summary.date}</b>\n\n"
            message += f"{summary.summary_text}\n\n"
            
            if summary.key_topics:
                key_topics = '\n'.join(summary.key_topics)
                message += f"🔑 <b>Key Topics:</b>\n{key_topics}\n\n"
            
            message += f"📊 Based on {summary.news_count} news items"
            
            # Send to all subscribers
            success_count = 0
            for user_id_str in subscribers:
                try:
                    user_id = int(user_id_str)
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='HTML'
                    )
                    success_count += 1
                except TelegramError as e:
                    logger.warning(f"Failed to send message to user {user_id_str}: {e}")
                    # Remove inactive users
                    if "chat not found" in str(e).lower() or "user is deactivated" in str(e).lower():
                        redis_client.redis_client.srem("subscribers", user_id_str)
                        redis_client.delete(f"user:{user_id_str}")
            
            logger.info(f"Sent summary to {success_count}/{len(subscribers)} subscribers")
            
        except Exception as e:
            logger.error(f"Error sending summary to subscribers: {e}")
    
    async def _poll_updates(self):
        """Poll for updates from Telegram."""
        while self.running:
            try:
                # Get updates
                updates = await self.bot.get_updates(
                    offset=self._last_update_id + 1,
                    timeout=10
                )
                
                for update in updates:
                    self._last_update_id = update.update_id
                    await self._handle_update(update)
                
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error polling updates: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def start_bot(self):
        """Start the bot."""
        try:
            logger.info("Starting Telegram bot...")
            
            # Test bot connection
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connected: {bot_info.first_name} (@{bot_info.username})")
            
            # Check and delete webhook if set
            webhook_info = await self.bot.get_webhook_info()
            if webhook_info.url:
                logger.info("Webhook detected, deleting it for polling...")
                await self.bot.delete_webhook()
                logger.info("Webhook deleted successfully")
            
            # Start polling
            self.running = True
            asyncio.create_task(self._poll_updates())
            
            logger.info("Telegram bot started successfully and polling for updates")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the bot."""
        try:
            logger.info("Stopping Telegram bot...")
            self.running = False
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}")


# Global bot instance
bot = MarketTwitsBot()