"""FastAPI server for Telegram bot endpoints."""

from datetime import datetime
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from ..models.schemas import (
    SubscriptionRequest, 
    SummaryResponse, 
    UserSubscription,
    Summary
)
from ..utils.config import config
from ..utils.logger import logger
from ..utils.redis_client import redis_client
from ..llm_module.summarizer import NewsSummarizer
from ..models.schemas import Summary


# Initialize FastAPI app
app = FastAPI(
    title="MarketTwits Summarizer API",
    description="API for MarketTwits news summarization service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize summarizer
summarizer = NewsSummarizer()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MarketTwits Summarizer API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Redis connection
        redis_client.redis_client.ping()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/subscribe", response_model=dict)
async def subscribe_user(request: SubscriptionRequest):
    """Subscribe a user to receive daily summaries."""
    try:
        logger.info(f"Subscribing user {request.user_id}")
        
        # Create user subscription
        subscription = UserSubscription(
            user_id=request.user_id,
            username=request.username
        )
        
        # Save to Redis
        redis_key = f"user:{request.user_id}"
        redis_client.set(redis_key, subscription.model_dump())
        
        # Add to subscribers set
        redis_client.add_to_set("subscribers", str(request.user_id))
        
        logger.info(f"Successfully subscribed user {request.user_id}")
        
        return {
            "success": True,
            "message": "Successfully subscribed to daily summaries",
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Failed to subscribe user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to subscribe user")


@app.delete("/unsubscribe/{user_id}")
async def unsubscribe_user(user_id: int):
    """Unsubscribe a user from daily summaries."""
    try:
        logger.info(f"Unsubscribing user {user_id}")
        
        # Remove from Redis
        redis_key = f"user:{user_id}"
        redis_client.delete(redis_key)
        
        # Remove from subscribers set
        redis_client.redis_client.srem("subscribers", str(user_id))
        
        logger.info(f"Successfully unsubscribed user {user_id}")
        
        return {
            "success": True,
            "message": "Successfully unsubscribed from daily summaries",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Failed to unsubscribe user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to unsubscribe user")


@app.get("/subscribers", response_model=List[int])
async def get_subscribers():
    """Get list of all subscribers."""
    try:
        subscribers = redis_client.get_set_members("subscribers")
        return [int(user_id) for user_id in subscribers if user_id.isdigit()]
    except Exception as e:
        logger.error(f"Failed to get subscribers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscribers")


@app.get("/summary/latest", response_model=SummaryResponse)
async def get_latest_summary():
    """Get the latest daily summary from Redis."""
    try:
        logger.info("Fetching latest summary from Redis")
        
        # Get latest summary from Redis
        summary_data = redis_client.get_json("latest_summary")
        
        if not summary_data:
            return SummaryResponse(
                success=False,
                message="No summary available yet"
            )
        
        # Convert to Summary object
        summary = Summary(**summary_data)
        
        return SummaryResponse(
            success=True,
            summary=summary,
            message="Latest summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to get latest summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get latest summary")


@app.get("/summary/{date}", response_model=SummaryResponse)
async def get_summary_by_date(date: str):
    """Get summary for a specific date (YYYY-MM-DD format) from Redis."""
    try:
        # Parse date
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        logger.info(f"Fetching summary for {date} from Redis")
        
        # Get summary from Redis by date
        date_str = target_date.strftime('%Y%m%d')
        redis_key = f"summary:{date_str}"
        summary_data = redis_client.get_json(redis_key)
        
        if not summary_data:
            return SummaryResponse(
                success=False,
                message=f"No summary available for {date}"
            )
        
        # Convert to Summary object
        summary = Summary(**summary_data)
        
        return SummaryResponse(
            success=True,
            summary=summary,
            message=f"Summary for {date} retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get summary for {date}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get summary")


@app.get("/summary", response_model=SummaryResponse)
async def get_summary():
    """Get summary for today or latest available from Redis."""
    try:
        # Try to get today's summary first
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        redis_key = f"summary:{date_str}"
        summary_data = redis_client.get_json(redis_key)
        
        # If no summary for today, get the latest
        if not summary_data:
            summary_data = redis_client.get_json("latest_summary")
        
        if not summary_data:
            return SummaryResponse(
                success=False,
                message="No summary available"
            )
        
        # Convert to Summary object
        summary = Summary(**summary_data)
        
        return SummaryResponse(
            success=True,
            summary=summary,
            message="Summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to get summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get summary")


@app.get("/news/all")
async def get_all_news(days_ago: int = 1, limit: int = 100):
    """Get news items using the same logic as summarization."""
    try:
        from datetime import datetime, timedelta
        from ..dumper.telegram_dumper import TelegramDumper
        
        # Calculate date range (same logic as summarization)
        # For summarization, we want news from the previous day by default
        target_date = datetime.now() - timedelta(days=days_ago)
        
        # Get news for the target date (same logic as summarization)
        dumper = TelegramDumper(session_name=config.TELEGRAM_SESSION_NAME_API)
        news_batch = dumper.get_news_for_date(target_date.date())
        
        if not news_batch or not news_batch.items:
            return {
                "success": False,
                "message": f"No news found for {target_date.date()}",
                "news_items": [],
                "total_count": 0
            }
        
        # Get limited number of items
        news_items = news_batch.items[:limit]
        
        return {
            "success": True,
            "total_count": len(news_batch.items),
            "returned_count": len(news_items),
            "date": target_date.date().isoformat(),
            "news_items": [item.model_dump() for item in news_items],
            "message": f"Retrieved {len(news_items)} news items for {target_date.date()}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get all news: {e}")
        raise HTTPException(status_code=500, detail="Failed to get all news")


@app.get("/news/count")
async def get_news_count(days_ago: int = 1):
    """Get count of news items using the same logic as summarization."""
    try:
        from datetime import datetime, timedelta
        from ..dumper.telegram_dumper import TelegramDumper
        
        # Calculate date range (same logic as summarization)
        # For summarization, we want news from the previous day by default
        target_date = datetime.now() - timedelta(days=days_ago)
        
        # Get news for the target date (same logic as summarization)
        dumper = TelegramDumper(session_name=config.TELEGRAM_SESSION_NAME_API)
        news_batch = dumper.get_news_for_date(target_date.date())
        
        if not news_batch:
            count = 0
        else:
            count = len(news_batch.items)
        
        return {
            "success": True,
            "total_count": count,
            "date": target_date.date().isoformat(),
            "message": f"Total news items for {target_date.date()}: {count}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get news count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get news count")


@app.get("/news/preview")
async def get_news_preview(days_ago: int = 1, limit: int = 10):
    """Get preview of news items that would go to summarization."""
    try:
        from datetime import datetime, timedelta
        from ..dumper.telegram_dumper import TelegramDumper
        from ..llm_module.summarizer import NewsSummarizer
        
        # Calculate date range (same logic as summarization)
        # For summarization, we want news from the previous day by default
        target_date = datetime.now() - timedelta(days=days_ago)
        
        # Get news for the target date
        dumper = TelegramDumper(session_name=config.TELEGRAM_SESSION_NAME_API)
        news_batch = dumper.get_news_for_date(target_date.date())
        
        if not news_batch or not news_batch.items:
            return {
                "success": False,
                "message": f"No news found for {target_date.date()}",
                "news_items": [],
                "total_count": 0
            }
        
        # Get limited number of items for preview
        preview_items = news_batch.items[:limit]
        
        # Show what would be sent to summarization
        news_texts = [item.text for item in preview_items if item.text.strip()]
        
        return {
            "success": True,
            "message": f"Preview of {len(preview_items)} news items for summarization",
            "date": target_date.date().isoformat(),
            "total_available": len(news_batch.items),
            "preview_count": len(preview_items),
            "news_items": [
                {
                    "id": item.message_id,
                    "text": item.text,
                    "date": item.date.isoformat(),
                    "views": item.views,
                    "forwards": item.forwards
                }
                for item in preview_items
            ],
            "sample_texts": news_texts[:5]  # First 5 texts that would go to AI
        }
        
    except Exception as e:
        logger.error(f"Failed to get news preview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get news preview")


@app.get("/news/summarization-preview")
async def get_summarization_preview(days_ago: int = 1):
    """Get preview of what would be sent to AI for summarization."""
    try:
        from datetime import datetime, timedelta
        from ..dumper.telegram_dumper import TelegramDumper
        from ..llm_module.summarizer import NewsSummarizer
        
        # Calculate date range (same logic as summarization)
        # For summarization, we want news from the previous day by default
        target_date = datetime.now() - timedelta(days=days_ago)
        
        # Get news for the target date
        dumper = TelegramDumper(session_name=config.TELEGRAM_SESSION_NAME_API)
        news_batch = dumper.get_news_for_date(target_date.date())
        
        if not news_batch or not news_batch.items:
            return {
                "success": False,
                "message": f"No news found for {target_date.date()}",
                "prompt_preview": "",
                "news_count": 0
            }
        
        # Extract text from news items (same logic as summarizer)
        news_texts = [item.text for item in news_batch.items if item.text.strip()]
        
        if not news_texts:
            return {
                "success": False,
                "message": "No text content found in news items",
                "prompt_preview": "",
                "news_count": 0
            }
        
        # Limit text length to avoid token limits (same logic as summarizer)
        max_text_length = 8000
        combined_text = "\n\n".join(news_texts)
        if len(combined_text) > max_text_length:
            combined_text = combined_text[:max_text_length] + "..."
            news_texts = [combined_text]
        
        # Create prompt preview
        summarizer = NewsSummarizer()
        last_date = target_date.strftime("%Y-%m-%d")
        prompt = summarizer._create_summarization_prompt(news_texts, last_date)
        
        return {
            "success": True,
            "message": f"Summarization preview for {target_date.date()}",
            "date": target_date.date().isoformat(),
            "news_count": len(news_batch.items),
            "text_count": len(news_texts),
            "total_text_length": len(combined_text),
            "truncated": len(combined_text) > max_text_length,
            "prompt_preview": prompt,
            "sample_news": [
                {
                    "id": item.message_id,
                    "text": item.text[:200] + "..." if len(item.text) > 200 else item.text,
                    "date": item.date.isoformat()
                }
                for item in news_batch.items[:5]
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get summarization preview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get summarization preview")


@app.post("/news/generate-summary")
async def generate_summary_now(days_ago: int = 1):
    """Generate summary for a specific date without caching (real-time)."""
    try:
        from datetime import datetime, timedelta
        from ..dumper.telegram_dumper import TelegramDumper
        from ..llm_module.summarizer import NewsSummarizer
        
        # Calculate target date
        target_date = datetime.now() - timedelta(days=days_ago)
        
        logger.info(f"Generating real-time summary for {target_date.date()}")
        
        # Get news for the target date
        dumper = TelegramDumper(session_name=config.TELEGRAM_SESSION_NAME_API)
        news_batch = dumper.get_news_for_date(target_date.date())
        
        if not news_batch or not news_batch.items:
            return {
                "success": False,
                "message": f"No news found for {target_date.date()}",
                "summary": None
            }
        
        # Create summary using AI
        summarizer = NewsSummarizer()
        summary = await summarizer.summarize_news(news_batch)
        
        if not summary:
            return {
                "success": False,
                "message": "Failed to generate summary",
                "summary": None
            }
        
        logger.info(f"Successfully generated real-time summary for {target_date.date()}")
        
        return {
            "success": True,
            "message": f"Summary generated for {target_date.date()}",
            "summary": summary.model_dump(),
            "news_count": len(news_batch.items),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.telegram_server.api:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
