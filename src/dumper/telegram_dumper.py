"""Telegram channel dumper for MarketTwits news using Telethon."""

import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

from ..models.schemas import NewsItem, NewsBatch
from ..utils.config import config
from ..utils.logger import logger
from ..utils.redis_client import redis_client


class TelegramDumper:
    """Dumps news from Telegram channel using Telethon."""
    
    def __init__(self):
        """Initialize the Telegram dumper."""
        self.api_id = config.TELEGRAM_API_ID
        self.api_hash = config.TELEGRAM_API_HASH
        self.channel_username = config.TELEGRAM_CHANNEL_USERNAME
        self.data_dir = config.DATA_DIR
        self.news_file = os.path.join(self.data_dir, "all_news.json")
        
        # Always use StringSession to avoid SQLite database locking issues
        logger.info("Using StringSession for Telegram client (no SQLite file)")
        self.client = TelegramClient(
            StringSession(config.TELEGRAM_SESSION_STRING),
            self.api_id,
            self.api_hash
        )
        
        self._is_connected = False
        self._connection_lock = asyncio.Lock()
        os.makedirs(self.data_dir, exist_ok=True)
        self._initialize_news_file()
    
    def _initialize_news_file(self):
        """Initialize the news file if it doesn't exist."""
        if not os.path.exists(self.news_file):
            initial_data = {
                "news_items": [],
                "last_updated": None,
                "total_count": 0
            }
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, default=str, ensure_ascii=False, indent=2)
            logger.info(f"Initialized news file at {self.news_file}")
    
    def _load_news_data(self) -> dict:
        """Load all news data from the JSON file."""
        try:
            with open(self.news_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load news data: {e}")
            return {"news_items": [], "last_updated": None, "total_count": 0}
    
    def _save_news_data(self, data: dict) -> bool:
        """Save all news data to the JSON file."""
        try:
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, default=str, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save news data: {e}")
            return False
    
    def _parse_media(self, media) -> Optional[dict]:
        """Parse media information from message."""
        if media is None:
            return None
            
        media_info = {}
        if isinstance(media, MessageMediaPhoto):
            media_info['type'] = 'photo'
            if hasattr(media, 'photo'):
                media_info['id'] = media.photo.id
                
        elif isinstance(media, MessageMediaDocument):
            media_info['type'] = 'document'
            if hasattr(media.document, 'attributes'):
                for attr in media.document.attributes:
                    if hasattr(attr, 'file_name'):
                        media_info['file_name'] = attr.file_name
            media_info['mime_type'] = media.document.mime_type
            media_info['size'] = media.document.size
            
        return media_info
    
    async def connect(self):
        """Connect to Telegram if not already connected."""
        async with self._connection_lock:
            if self._is_connected:
                logger.debug("Already connected to Telegram")
                return True
            
            try:
                # Connect using StringSession (no file needed)
                logger.info("Connecting to Telegram using StringSession...")
                await asyncio.wait_for(self.client.start(), timeout=15)
                self._is_connected = True
                logger.info("Connected to Telegram successfully")
                return True
            except asyncio.TimeoutError:
                logger.error("Connection to Telegram timed out after 15 seconds")
                self._is_connected = False
                return False
            except Exception as e:
                logger.error(f"Failed to connect to Telegram: {e}")
                self._is_connected = False
                return False
    
    async def disconnect(self):
        """Disconnect from Telegram."""
        async with self._connection_lock:
            if not self._is_connected:
                logger.debug("Already disconnected from Telegram")
                return
            
            try:
                await self.client.disconnect()
                self._is_connected = False
                logger.info("Disconnected from Telegram")
            except Exception as e:
                logger.error(f"Error disconnecting from Telegram: {e}")
    
    async def ensure_connected(self):
        """Ensure Telegram connection is established."""
        if not self._is_connected:
            return await self.connect()
        return True
    
    def is_connected(self):
        """Check if currently connected to Telegram."""
        return self._is_connected
    
    async def close(self):
        """Close the dumper and disconnect from Telegram."""
        await self.disconnect()
    
    async def get_channel_messages(
        self, 
        from_date: Optional[datetime] = None, 
        limit: int = 100
    ) -> List[NewsItem]:
        """Get messages from the Telegram channel."""
        try:
            # Ensure we're connected
            if not await self.ensure_connected():
                logger.error("Failed to connect to Telegram")
                return []
            
            logger.info(f"Fetching messages from {self.channel_username}")
            
            # Get the channel entity
            try:
                channel = await self.client.get_entity(self.channel_username)
            except Exception as e:
                logger.error(f"Failed to get channel entity: {e}")
                return []
            
            messages = []
            message_count = 0
            
            # Fetch messages
            async for message in self.client.iter_messages(
                channel,
                offset_date=from_date,
                limit=limit
            ):
                if message.text:  # Only process messages with text
                    # Parse media information
                    media_info = self._parse_media(message.media)
                    
                    # Create NewsItem
                    news_item = NewsItem(
                        message_id=message.id,
                        text=message.text,
                        date=message.date,
                        views=getattr(message, 'views', None),
                        forwards=getattr(message, 'forwards', None)
                    )
                    
                    messages.append(news_item)
                    message_count += 1
                    
                    if message_count >= limit:
                        break
            
            logger.info(f"Successfully fetched {len(messages)} messages")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get channel messages: {e}")
            return []
    
    def save_news_batch(self, news_batch: NewsBatch) -> bool:
        """Save news batch to the unified JSON file and Redis."""
        try:
            # Load existing data
            data = self._load_news_data()
            
            # Convert NewsItem objects to dictionaries
            new_items = [item.model_dump() for item in news_batch.items]
            
            # Add new items to existing data
            data["news_items"].extend(new_items)
            data["last_updated"] = news_batch.end_date.isoformat()
            data["total_count"] = len(data["news_items"])
            
            # Remove duplicates based on message_id
            seen_ids = set()
            unique_items = []
            for item in data["news_items"]:
                if item["message_id"] not in seen_ids:
                    seen_ids.add(item["message_id"])
                    unique_items.append(item)
            
            data["news_items"] = unique_items
            data["total_count"] = len(unique_items)
            
            # Save to file
            if not self._save_news_data(data):
                return False
            
            logger.info(f"Saved {len(new_items)} news items to unified file. Total: {data['total_count']}")
            
            # Save to Redis for quick access
            redis_client.set("all_news", data, expire=86400 * 7)  # 7 days
            
            # Update latest timestamp
            redis_client.set("latest_news_timestamp", news_batch.end_date.isoformat())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save news batch: {e}")
            return False
    
    def load_latest_timestamp(self) -> Optional[datetime]:
        """Load the latest processed timestamp from Redis or file."""
        try:
            # Try Redis first
            timestamp_str = redis_client.get("latest_news_timestamp")
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str)
            
            # Fallback to file system
            data = self._load_news_data()
            if data.get("last_updated"):
                return datetime.fromisoformat(data["last_updated"])
            
            # Default to last month if no data
            return datetime.now() - timedelta(days=10)
            
        except Exception as e:
            logger.error(f"Failed to load latest timestamp: {e}")
            return datetime.now() - timedelta(days=10)
    
    async def dump_news(self, from_date: Optional[datetime] = None) -> bool:
        """Main method to dump news from Telegram channel."""
        try:
            if from_date is None:
                from_date = self.load_latest_timestamp()
            
            logger.info(f"Starting news dump from {from_date}")
            
            # Get messages (connection is handled internally)
            messages = await self.get_channel_messages(from_date=from_date, limit=1000)
            
            if not messages:
                logger.warning("No new messages found")
                return True
            
            # Create news batch
            news_batch = NewsBatch(
                items=messages,
                start_date=from_date,
                end_date=datetime.now(),
                total_count=len(messages)
            )
            
            # Save the batch
            success = self.save_news_batch(news_batch)
            
            if success:
                logger.info(f"Successfully dumped {len(messages)} news items")
            else:
                logger.error("Failed to save news batch")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to dump news: {e}")
            return False
    
    def get_news_for_date(self, target_date: datetime) -> Optional[NewsBatch]:
        """Get news batch for a specific date."""
        try:
            # Try Redis first
            data = redis_client.get_json("all_news")
            if not data:
                # Fallback to file system
                data = self._load_news_data()
            
            if not data or not data.get("news_items"):
                return None
            
            # Filter news items for the target date
            target_date_str = target_date.strftime('%Y-%m-%d')
            filtered_items = []
            
            for item_data in data["news_items"]:
                item_date = datetime.fromisoformat(item_data["date"]).strftime('%Y-%m-%d')
                if item_date == target_date_str:
                    # Convert dict back to NewsItem
                    news_item = NewsItem(**item_data)
                    filtered_items.append(news_item)
            
            if not filtered_items:
                return None
            
            # Create NewsBatch for the filtered items
            return NewsBatch(
                items=filtered_items,
                start_date=target_date,
                end_date=target_date,
                total_count=len(filtered_items)
            )
            
        except Exception as e:
            logger.error(f"Failed to get news for date {target_date}: {e}")
            return None
    
    def get_all_news(self) -> List[NewsItem]:
        """Get all news items from the unified file."""
        try:
            data = self._load_news_data()
            if not data or not data.get("news_items"):
                return []
            
            # Convert dict items back to NewsItem objects
            news_items = []
            for item_data in data["news_items"]:
                try:
                    news_item = NewsItem(**item_data)
                    news_items.append(news_item)
                except Exception as e:
                    logger.warning(f"Failed to parse news item: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.error(f"Failed to get all news: {e}")
            return []
    
    def get_news_count(self) -> int:
        """Get total number of news items."""
        try:
            data = self._load_news_data()
            return data.get("total_count", 0)
        except Exception as e:
            logger.error(f"Failed to get news count: {e}")
            return 0