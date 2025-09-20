# MarketTwits Summarizer

A Python-based system that automatically fetches financial news from a Telegram channel, summarizes them using OpenAI's LLM, and provides daily summaries to subscribed users.

## Features

- **Telegram Integration**: Fetches news from @MarketTwits channel using Telethon
- **Telegram Bot**: Interactive bot for user subscriptions and notifications
- **AI Summarization**: Uses OpenAI GPT models to create concise daily summaries
- **Redis Caching**: Efficient caching and data storage
- **REST API**: FastAPI-based server with subscription management
- **Scheduled Processing**: Daily 7 AM (UTC+3) news processing and distribution
- **Docker Support**: Fully containerized with Docker Compose
- **Comprehensive Logging**: Structured logging with Loguru
- **Testing**: Unit and integration tests with pytest

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   FastAPI       │    │   Redis         │
│   Channel       │───▶│   Server        │───▶│   Cache         │
│   (@MarketTwits)│    │   (Port 8000)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   Telegram Bot  │              │
         │              │   (User Bot)    │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telethon      │    │   Users         │    │   OpenAI API    │
│   Client        │    │   (Subscribers) │    │   (Summarizer)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

1. **Telegram Server** (`src/telegram_server/`): FastAPI server with subscription and summary endpoints
2. **Telegram Bot** (`src/telegram_bot/`): Interactive bot for user subscriptions and notifications
3. **Dumper** (`src/dumper/`): Fetches news from Telegram channel using Telethon
4. **LLM Module** (`src/llm_module/`): OpenAI-based news summarization
5. **Scheduler** (`src/scheduler/`): Daily job processing at 7 AM
6. **Utils** (`src/utils/`): Configuration, logging, and Redis client

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Telegram API ID and API Hash (from https://my.telegram.org/apps)
- Telegram Bot Token (from @BotFather)
- OpenAI API Key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd MarketTwitsSummarizer
```

### 2. Environment Configuration

```bash
cp env.example .env
```

Edit `.env` with your credentials:

```env
TELEGRAM_API_ID=your_telegram_api_id_here
TELEGRAM_API_HASH=your_telegram_api_hash_here
TELEGRAM_CHANNEL_USERNAME=MarketTwits
TELEGRAM_SESSION_NAME=market_twits_parser
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

### 4. Run Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (if not using Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Run the application
python main.py
```

## API Endpoints

### Health Check
- `GET /health` - Check service health

### Subscription Management
- `POST /subscribe` - Subscribe to daily summaries
- `DELETE /unsubscribe/{user_id}` - Unsubscribe from summaries
- `GET /subscribers` - Get list of subscribers

### Summary Retrieval
- `GET /summary` - Get latest summary
- `GET /summary/latest` - Get latest summary (alias)
- `GET /summary/{date}` - Get summary for specific date (YYYY-MM-DD)

### News Data
- `GET /news/all` - Get all news items from unified storage
- `GET /news/count` - Get total count of news items

### Example Usage

```bash
# Subscribe a user
curl -X POST "http://localhost:8000/subscribe" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 12345, "username": "john_doe"}'

# Get latest summary
curl "http://localhost:8000/summary/latest"

# Get summary for specific date
curl "http://localhost:8000/summary/2024-01-15"

# Get all news items
curl "http://localhost:8000/news/all"

# Get news count
curl "http://localhost:8000/news/count"
```

## Telegram Bot Commands

The system includes a Telegram bot for user interaction. Users can interact with the bot using these commands:

- `/start` - Start using the bot and subscribe to daily summaries
- `/help` - Show help message with all available commands
- `/subscribe` - Subscribe to daily summaries
- `/unsubscribe` - Unsubscribe from summaries
- `/summary` - Get today's summary
- `/latest` - Get the latest available summary
- `/stats` - Show news statistics

### Bot Features

- **Automatic Subscription**: Users are automatically subscribed when they start the bot
- **Daily Notifications**: Sends summaries every day at 7 AM (UTC+3)
- **Interactive Buttons**: Inline keyboard for easy navigation
- **Smart Responses**: Understands natural language queries
- **User Management**: Tracks subscribers and handles unsubscriptions

## CLI Tools

The system includes a command-line interface for manual operations:

```bash
# Dump news manually
python cli.py dump --days-ago 1

# Create summary for specific date
python cli.py summary --date 2024-01-15

# Run daily job manually
python cli.py daily-job

# Show news statistics
python cli.py stats

# Test Telegram bot
python cli.py test-bot

# Send test summary to subscribers
python cli.py send-test
```

## Configuration

The application uses environment variables for configuration. See `env.example` for all available options.

### Key Settings

- `TELEGRAM_API_ID`: Your Telegram API ID (from https://my.telegram.org/apps)
- `TELEGRAM_API_HASH`: Your Telegram API hash (from https://my.telegram.org/apps)
- `TELEGRAM_CHANNEL_USERNAME`: Target channel username (e.g., MarketTwits)
- `TELEGRAM_SESSION_NAME`: Session name for Telegram client (default: market_twits_parser)
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (from @BotFather)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-3.5-turbo)
- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `SCHEDULER_TIMEZONE`: Timezone for scheduler (default: Europe/Moscow for UTC+3)

### Getting Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your Telegram account
3. Create a new application:
   - App title: "MarketTwits Summarizer"
   - Short name: "market_twits"
   - Platform: "Desktop"
4. Copy the `api_id` and `api_hash` to your `.env` file

### Getting Telegram Bot Token

1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow the instructions to create a new bot
4. Copy the bot token to your `.env` file

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_summarizer.py
```

### Code Structure

```
src/
├── models/           # Pydantic models and schemas
├── utils/            # Configuration, logging, Redis client
├── dumper/           # Telegram news dumper
├── llm_module/       # OpenAI summarization
├── telegram_server/  # FastAPI server
└── scheduler/        # Daily job scheduler

tests/
├── unit/             # Unit tests
└── integration/      # Integration tests
```

### Adding New Features

1. Create feature branch
2. Add tests for new functionality
3. Implement the feature
4. Update documentation
5. Submit pull request

## Monitoring and Logs

- Application logs: `logs/market_twits.log`
- Error logs: `logs/errors.log`
- Health check: `GET /health`
- Redis monitoring: Use Redis CLI or GUI tools

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Ensure Redis is running: `docker ps`
   - Check Redis configuration in `.env`

2. **Telegram API Errors**
   - Verify API ID and API hash are correct
   - Check channel username format (MarketTwits)
   - Ensure you have access to the channel

3. **OpenAI API Errors**
   - Verify API key is valid
   - Check API usage limits

4. **Scheduler Not Running**
   - Check timezone configuration
   - Verify scheduler is started in logs

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the logs for error details
- Verify configuration settings
