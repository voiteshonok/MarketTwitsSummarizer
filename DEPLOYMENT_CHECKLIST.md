# Deployment Checklist

## ✅ Pre-Deployment Setup

### 1. Generate Session String
```bash
python generate_session_string.py
```
- [ ] Generated SESSION_STRING
- [ ] Saved to `.env` file

### 2. Configure Environment
Edit `.env` file with all required values:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_CHANNEL_USERNAME=MarketTwits
TELEGRAM_SESSION_STRING=your_session_string
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo
REDIS_HOST=redis
REDIS_PORT=6379
SCHEDULER_TIMEZONE=Europe/Moscow
```

- [ ] All credentials configured
- [ ] SESSION_STRING added
- [ ] Redis configuration correct

### 3. Set Up Permissions (Docker/Production)
```bash
# Create directories
mkdir -p data logs

# Set permissions
sudo chown -R 1000:1000 data/ logs/
chmod -R 775 data/ logs/
```

- [ ] Directories created
- [ ] Permissions set correctly

## 🚀 Deployment

### Local Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

- [ ] Dependencies installed
- [ ] Application starts without errors
- [ ] No "database is locked" errors

### Docker Deployment
```bash
# Build and start
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs app
```

- [ ] Docker images built successfully
- [ ] Containers running
- [ ] No errors in logs
- [ ] No "database is locked" errors

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```
- [ ] Returns healthy status

### API Tests
```bash
# Test news count
curl -X GET "http://localhost:8000/news/count?days_ago=1"

# Test summary generation
curl -X POST "http://localhost:8000/news/generate-summary?days_ago=1"

# Test latest summary
curl -X GET "http://localhost:8000/summary/latest"
```

- [ ] All endpoints respond correctly
- [ ] No 500 errors
- [ ] No "database is locked" errors

### Bot Test
Send commands to your bot:
- [ ] `/start` - Bot responds with welcome message
- [ ] `/help` - Shows help information
- [ ] `/latest` - Returns latest summary
- [ ] `/subscribe` - Subscribes user

## 📊 Monitoring

### Check Logs
```bash
# Docker
docker-compose logs -f app

# Local
tail -f logs/market_twits.log
```

- [ ] No error messages
- [ ] Scheduler jobs configured correctly
- [ ] Bot polling for updates

### Verify Scheduler
```bash
# Check scheduler logs for next job times
docker-compose logs app | grep -i "scheduled for"
```

- [ ] News dump scheduled for 15:00 Europe/Moscow
- [ ] Summary push scheduled for 15:07 Europe/Moscow

## 🎯 Success Criteria

- ✅ Application starts without errors
- ✅ No SQLite "database is locked" errors
- ✅ All API endpoints working
- ✅ Bot responding to commands
- ✅ Scheduler jobs configured
- ✅ Redis connection established
- ✅ Logs being written properly

## 🔧 Common Issues

### Issue: "Missing required environment variables"
**Solution:** Check that SESSION_STRING is in .env file

### Issue: "Invalid session"
**Solution:** Regenerate SESSION_STRING with `python generate_session_string.py`

### Issue: "Permission denied" (Docker)
**Solution:** Run `sudo chown -R 1000:1000 data/ logs/`

### Issue: "Port already in use"
**Solution:** Change port in docker-compose.yml or stop conflicting service

## 📝 Notes

- StringSession eliminates all SQLite locking issues
- Multiple processes can now run simultaneously
- Works perfectly in Docker containers
- No .session files needed anymore
