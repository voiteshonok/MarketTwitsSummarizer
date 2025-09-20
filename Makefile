# MarketTwits Summarizer Makefile

.PHONY: help install test run docker-build docker-up docker-down clean

help: ## Show this help message
	@echo "MarketTwits Summarizer - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio pytest-mock

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

run: ## Run the application
	python main.py

run-cli: ## Run CLI tool
	python cli.py --help

docker-build: ## Build Docker image
	docker build -t market-twits-summarizer .

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop services with Docker Compose
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage

setup-env: ## Copy environment file
	cp env.example .env
	@echo "Please edit .env file with your configuration"

check-env: ## Check environment configuration
	python -c "from src.utils.config import config; config.validate(); print('Configuration is valid')"

dump-news: ## Dump news manually
	python cli.py dump

create-summary: ## Create summary manually
	python cli.py summary

daily-job: ## Run both daily jobs manually
	python cli.py daily-job

dump-job: ## Run dump job manually
	python cli.py dump-job

push-job: ## Run push job manually
	python cli.py push-job

show-stats: ## Show news statistics
	python cli.py stats

test-bot: ## Test Telegram bot functionality
	python cli.py test-bot

send-test: ## Send test summary to subscribers
	python cli.py send-test

clear-summary: ## Clear latest summary from Redis
	python cli.py clear-summary

clear-date: ## Clear summary for specific date (use: make clear-date DATE=2024-01-15)
	python cli.py clear-date --date $(DATE)

preview-news: ## Preview news items for summarization
	python cli.py preview-news

preview-summarization: ## Preview what would be sent to AI
	python cli.py preview-summarization

clear-news: ## Clear all news data from storage
	python cli.py clear-news

generate: ## Generate fresh summary without caching
	python cli.py generate

test-redis: ## Test Redis-based architecture
	python test_redis_approach.py

test-redis-retrieval: ## Test Redis summary retrieval
	python test_redis_retrieval.py

run-dumper: ## Run standalone dumper
	python standalone_dumper.py --daily
