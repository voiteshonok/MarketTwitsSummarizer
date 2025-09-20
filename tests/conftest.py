"""Pytest configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.models.schemas import NewsItem, NewsBatch, Summary
from src.utils.redis_client import RedisClient


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_news_item():
    """Create a mock news item."""
    return NewsItem(
        message_id=12345,
        text="Test news item about market movements",
        date=datetime.now(),
        views=100,
        forwards=5
    )


@pytest.fixture
def mock_news_batch(mock_news_item):
    """Create a mock news batch."""
    return NewsBatch(
        items=[mock_news_item],
        start_date=datetime.now(),
        end_date=datetime.now(),
        total_count=1
    )


@pytest.fixture
def mock_summary():
    """Create a mock summary."""
    return Summary(
        date=datetime.now().date(),
        summary_text="Test summary of market news",
        news_count=1,
        key_topics=["market", "trading", "finance"]
    )


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    mock_client = Mock(spec=RedisClient)
    mock_client.set = Mock(return_value=True)
    mock_client.get = Mock(return_value=None)
    mock_client.get_json = Mock(return_value=None)
    mock_client.delete = Mock(return_value=True)
    mock_client.exists = Mock(return_value=False)
    mock_client.set_hash = Mock(return_value=True)
    mock_client.get_hash = Mock(return_value={})
    mock_client.add_to_set = Mock(return_value=1)
    mock_client.get_set_members = Mock(return_value=set())
    mock_client.ping = Mock()
    return mock_client


@pytest.fixture
def mock_telegram_client():
    """Create a mock Telegram client."""
    mock_client = AsyncMock()
    mock_client.start = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.get_entity = AsyncMock()
    mock_client.iter_messages = AsyncMock()
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"summary": "Test summary", "key_topics": ["test"]}'
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client
