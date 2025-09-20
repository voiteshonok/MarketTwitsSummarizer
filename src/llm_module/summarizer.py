"""LLM-based news summarizer using OpenAI."""

import json
from datetime import datetime
from typing import List, Optional
from openai import AsyncOpenAI

from ..models.schemas import NewsBatch, Summary
from ..utils.config import config
from ..utils.logger import logger
from ..utils.redis_client import redis_client


class NewsSummarizer:
    """News summarizer using OpenAI API."""
    
    def __init__(self):
        """Initialize the summarizer."""
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    def _create_summarization_prompt(self, news_items: List[str], last_date: str = None) -> str:
        """Create a prompt for news summarization."""
        all_day_news = "\n".join([f"• {item}" for item in news_items])
        
        if not last_date:
            from datetime import datetime
            last_date = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
Сегодня {last_date}

Дай мне краткое резюме на основе твитов из новостного канала о финансовых рынках. Дай мне только основные новости о мировом рынке и политике, не используй российские новости, криптовалюты, мемы, кроме случаев, когда они важны.

ВОТ все твиты:
"
{all_day_news}
"

Используй формат как пронумерованный список кратких новостей, отсортированных от самых важных к менее важным.

Формат ответа в JSON:
{{
    "summary": "Краткий обзор самых важных рыночных событий",
    "key_topics": [используй формат нумерованного списка с самой важной новстью к менее важной]
]
}}

Фокусируйся на:
- Крупных движениях мировых рынков
- Важных политических событиях, влияющих на рынки
- Решениях центральных банков
- Экономических показателях
- Корпоративных доходах и крупных бизнес-новостях
- Геополитических событиях с рыночным воздействием

Исключи:
- Российские внутренние новости (если не глобально значимые)
- Новости о криптовалютах (если не имеют большого рыночного воздействия)
- Мемы и шутки (если не важны)
- Мелкие местные новости
- Спекуляции без содержания

Пиши на русском языке в формате пронумерованного списка.
"""
        return prompt
    
    async def summarize_news(self, news_batch: NewsBatch) -> Optional[Summary]:
        """Summarize a batch of news items."""
        try:
            logger.info(f"Summarizing {len(news_batch.items)} news items")
            
            # Extract text from news items
            news_texts = [item.text for item in news_batch.items if item.text.strip()]
            
            if not news_texts:
                logger.warning("No text content found in news items")
                return None
            
            # Limit text length to avoid token limits
            max_text_length = 8000  # Approximate token limit
            combined_text = "\n\n".join(news_texts)
            if len(combined_text) > max_text_length:
                # Truncate to fit within limits
                combined_text = combined_text[:max_text_length] + "..."
                news_texts = [combined_text]
            
            # Create prompt with date
            last_date = news_batch.end_date.strftime("%Y-%m-%d")
            prompt = self._create_summarization_prompt(news_texts, last_date)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional financial news analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                summary_data = json.loads(content)
                summary_text = summary_data.get("summary", content)
                key_topics = summary_data.get("key_topics", [])
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                summary_text = content
                key_topics = []
            
            # Create Summary object
            summary = Summary(
                date=news_batch.end_date.date(),
                summary_text=summary_text,
                news_count=len(news_batch.items),
                key_topics=key_topics
            )
            
            logger.info("Successfully created news summary")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize news: {e}")
            return None
    
    def save_summary(self, summary: Summary) -> bool:
        """Save summary to Redis cache."""
        try:
            # Save to Redis
            redis_key = f"summary:{summary.date.strftime('%Y%m%d')}"
            redis_client.set(redis_key, summary.model_dump(), expire=86400 * 30)  # 30 days
            
            # Update latest summary
            redis_client.set("latest_summary", summary.model_dump(), expire=86400 * 7)  # 7 days
            
            logger.info(f"Saved summary for {summary.date} to cache")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            return False
    
    def get_summary_for_date(self, target_date: datetime) -> Optional[Summary]:
        """Get summary for a specific date from cache."""
        try:
            redis_key = f"summary:{target_date.strftime('%Y%m%d')}"
            data = redis_client.get_json(redis_key)
            
            if data:
                return Summary(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get summary for date {target_date}: {e}")
            return None
    
    def get_latest_summary(self) -> Optional[Summary]:
        """Get the latest summary from cache."""
        try:
            data = redis_client.get_json("latest_summary")
            
            if data:
                return Summary(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest summary: {e}")
            return None
    
    async def process_news_batch(self, news_batch: NewsBatch) -> Optional[Summary]:
        """Process a news batch and return summary."""
        try:
            # Check if summary already exists
            existing_summary = self.get_summary_for_date(news_batch.end_date)
            if existing_summary:
                logger.info(f"Summary for {news_batch.end_date.date()} already exists")
                return existing_summary
            
            # Create new summary
            summary = await self.summarize_news(news_batch)
            if not summary:
                return None
            
            # Save summary
            self.save_summary(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to process news batch: {e}")
            return None
