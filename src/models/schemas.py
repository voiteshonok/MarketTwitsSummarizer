"""Pydantic models for the MarketTwits Summarizer."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """Model for a single news item from Telegram channel."""
    message_id: int
    text: str
    date: datetime
    views: Optional[int] = None
    forwards: Optional[int] = None


class NewsBatch(BaseModel):
    """Model for a batch of news items."""
    items: List[NewsItem]
    start_date: datetime
    end_date: datetime
    total_count: int


class Summary(BaseModel):
    """Model for the daily summary."""
    date: datetime
    summary_text: str
    news_count: int
    key_topics: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserSubscription(BaseModel):
    """Model for user subscription."""
    user_id: int
    username: Optional[str] = None
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class SubscriptionRequest(BaseModel):
    """Model for subscription request."""
    user_id: int
    username: Optional[str] = None


class SummaryResponse(BaseModel):
    """Model for summary response."""
    success: bool
    summary: Optional[Summary] = None
    message: str
