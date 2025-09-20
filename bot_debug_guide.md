# Telegram Bot Debug Guide

## Common Issues and Solutions

### 1. Bot Not Responding to Messages

**Possible Causes:**
- Bot token is incorrect
- Bot is not running
- Webhook is set (blocks polling)
- Bot doesn't have permission to receive messages
- Network/firewall issues

### 2. Step-by-Step Debugging

#### Step 1: Verify Bot Token
```bash
# Test bot connection
python simple_bot_test.py
```

#### Step 2: Check Bot Status
```bash
# Test with debug script
python debug_bot.py
```

#### Step 3: Check Webhook Status
```python
import asyncio
from telegram import Bot

async def check_webhook():
    bot = Bot(token="YOUR_BOT_TOKEN")
    webhook_info = await bot.get_webhook_info()
    print(f"Webhook URL: {webhook_info.url}")
    if webhook_info.url:
        print("Webhook is set - this blocks polling!")
        await bot.delete_webhook()
        print("Webhook deleted")

asyncio.run(check_webhook())
```

#### Step 4: Test Simple Bot
1. Edit `simple_bot_test.py`
2. Set your bot token
3. Run: `python simple_bot_test.py`
4. Send `/start` to your bot

#### Step 5: Check Logs
```bash
# Check application logs
tail -f logs/market_twits.log

# Check error logs
tail -f logs/errors.log
```

### 3. Bot Setup Checklist

- [ ] Bot token is correct
- [ ] Bot is created via @BotFather
- [ ] Bot is not in a group (test in private chat)
- [ ] No webhook is set
- [ ] Bot has permission to receive messages
- [ ] Network connection is working

### 4. Testing Commands

```bash
# Test bot connection
python cli.py test-bot

# Send test message
python cli.py send-test

# Check bot status
curl http://localhost:8000/health
```

### 5. Manual Bot Test

1. Start the application: `python main.py`
2. Check logs for "Telegram bot started successfully"
3. Send `/start` to your bot in Telegram
4. Check logs for incoming messages

### 6. Common Error Messages

- `Unauthorized`: Bot token is wrong
- `Chat not found`: Bot is not in the chat
- `Forbidden`: Bot doesn't have permission
- `Network error`: Connection issues

### 7. Quick Fixes

```bash
# Delete webhook (if set)
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"

# Get bot info
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"

# Get webhook info
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```
