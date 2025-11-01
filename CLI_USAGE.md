# CLI Usage Guide

## 📋 Available Commands

### News Dumping

#### Dump News from Telegram
```bash
# Dump news from last 1 day (default)
python cli.py dump

# Dump news from last 2 days
python cli.py dump --days-ago 2

# Dump news from last 7 days
python cli.py dump --days-ago 7
```

**What it does:**
- Fetches messages from Telegram channel
- Saves them to `data/all_news.json`
- Caches in Redis for quick access

#### In Docker
```bash
# Dump news from last 2 days
docker exec market_twits_app python cli.py dump --days-ago 2
```

### Summary Generation

#### Create Summary for Specific Date
```bash
# Create summary for a specific date
python cli.py summary --date 2025-09-20

# Create summary for yesterday
python cli.py summary --date $(date -d "yesterday" +%Y-%m-%d)
```

#### Generate Fresh Summary (Without Cache)
```bash
# Generate fresh summary for yesterday
python cli.py generate --days-ago 1

# Generate fresh summary for 2 days ago
python cli.py generate --days-ago 2
```

**Difference:**
- `summary`: Creates and saves summary to Redis
- `generate`: Creates fresh summary without checking cache (uses API)

### Daily Jobs

#### Run Both Daily Jobs
```bash
python cli.py daily-job
```

**What it does:**
1. Runs dump job (fetches news and creates summary)
2. Runs push job (sends summary to subscribers)

#### Run Individual Jobs
```bash
# Run only dump job
python cli.py dump-job

# Run only push job
python cli.py push-job
```

### Statistics & Preview

#### Show News Statistics
```bash
python cli.py stats
```

**Output:**
- Total news count
- Latest update timestamp
- News items by date

#### Preview Summarization
```bash
# Preview what would be summarized for yesterday
python cli.py preview-summarization --days-ago 1

# Preview for 2 days ago
python cli.py preview-summarization --days-ago 2
```

**What it shows:**
- News items that would be sent to AI
- Character count
- Preview of content

### Data Management

#### Clear All News Data
```bash
python cli.py clear-news
```

**What it does:**
- Backs up `all_news.json` to `all_news.json.backup`
- Creates fresh empty news file
- Clears all Redis cache (news + summaries)

**⚠️ Warning:** This clears all news and summaries!

#### Clear Specific Summary
```bash
python cli.py clear-summary --date 2025-09-20
```

#### Clear Latest Summary
```bash
python cli.py clear-latest
```

### Testing

#### Test Bot Functionality
```bash
python cli.py test-bot
```

#### Send Test Summary
```bash
python cli.py test-summary
```

## 🔧 Common Usage Scenarios

### Scenario 1: Fetch and Summarize Last 2 Days
```bash
# Step 1: Dump news
python cli.py dump --days-ago 2

# Step 2: Generate summaries
python cli.py generate --days-ago 1
python cli.py generate --days-ago 2
```

### Scenario 2: Daily Routine (Manual)
```bash
# Run both daily jobs manually
python cli.py daily-job
```

### Scenario 3: Check What's Available
```bash
# Check statistics
python cli.py stats

# Preview what would be summarized
python cli.py preview-summarization --days-ago 1
```

### Scenario 4: Fresh Start
```bash
# Clear all data
python cli.py clear-news

# Dump fresh news
python cli.py dump --days-ago 7

# Generate summaries
python cli.py generate --days-ago 1
```

## 🐳 Docker Usage

All commands work in Docker by prefixing with `docker exec`:

```bash
# Examples
docker exec market_twits_app python cli.py dump --days-ago 2
docker exec market_twits_app python cli.py generate --days-ago 1
docker exec market_twits_app python cli.py stats
docker exec market_twits_app python cli.py daily-job
```

## 💡 Tips

1. **Use `--days-ago`** to specify how far back to go
2. **Preview first** before generating summaries
3. **Check stats** to see what's available
4. **Clear cache** if you want fresh data
5. **Use daily-job** for scheduled operations

## 📝 Help

Get help for any command:
```bash
python cli.py --help
python cli.py dump --help
python cli.py generate --help
```
