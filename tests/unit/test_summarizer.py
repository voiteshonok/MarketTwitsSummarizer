"""Unit tests for the news summarizer."""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from src.llm_module.summarizer import NewsSummarizer
from src.models.schemas import NewsBatch, NewsItem


class TestNewsSummarizer:
    """Test cases for NewsSummarizer."""
    
    @pytest.fixture
    def summarizer(self, mock_redis_client):
        """Create a summarizer instance with mocked dependencies."""
        with patch('src.llm_module.summarizer.redis_client', mock_redis_client):
            return NewsSummarizer()
    
    @pytest.fixture
    def sample_news_batch(self):
        """Create a sample news batch for testing."""
        news_items = [
            NewsItem(
                message_id=1,
                text="Stock market rises 2% on positive earnings",
                date=datetime.now(),
                views=100,
                forwards=5
            ),
            NewsItem(
                message_id=2,
                text="Federal Reserve hints at rate cuts",
                date=datetime.now(),
                views=150,
                forwards=10
            )
        ]
        
        return NewsBatch(
            items=news_items,
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_count=2
        )
    
    @pytest.mark.asyncio
    async def test_summarize_news_success(self, summarizer, sample_news_batch, mock_openai_client):
        """Test successful news summarization."""
        with patch.object(summarizer, 'client', mock_openai_client):
            result = await summarizer.summarize_news(sample_news_batch)
            
            assert result is not None
            assert result.summary_text == "Test summary"
            assert result.key_topics == ["test"]
            assert result.news_count == 2
    
    @pytest.mark.asyncio
    async def test_summarize_news_empty_text(self, summarizer, mock_redis_client):
        """Test summarization with empty news text."""
        empty_news_batch = NewsBatch(
            items=[
                NewsItem(
                    message_id=1,
                    text="",
                    date=datetime.now()
                )
            ],
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_count=1
        )
        
        result = await summarizer.summarize_news(empty_news_batch)
        assert result is None
    
    def test_save_summary(self, summarizer, mock_redis_client):
        """Test saving summary to cache."""
        from src.models.schemas import Summary
        
        summary = Summary(
            date=datetime.now().date(),
            summary_text="Test summary",
            news_count=1,
            key_topics=["test"]
        )
        
        result = summarizer.save_summary(summary)
        assert result is True
        assert mock_redis_client.set.call_count == 2  # summary + latest_summary
    
    def test_get_summary_for_date(self, summarizer, mock_redis_client):
        """Test getting summary for specific date."""
        target_date = datetime.now()
        mock_redis_client.get_json.return_value = {
            "date": target_date.strftime("%Y-%m-%d"),
            "summary_text": "Test summary",
            "news_count": 1,
            "key_topics": ["test"],
            "created_at": datetime.now().isoformat()
        }
        
        result = summarizer.get_summary_for_date(target_date)
        assert result is not None
        assert result.summary_text == "Test summary"
    
    def test_get_latest_summary(self, summarizer, mock_redis_client):
        """Test getting latest summary."""
        mock_redis_client.get_json.return_value = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary_text": "Latest summary",
            "news_count": 1,
            "key_topics": ["latest"],
            "created_at": datetime.now().isoformat()
        }
        
        result = summarizer.get_latest_summary()
        assert result is not None
        assert result.summary_text == "Latest summary"
