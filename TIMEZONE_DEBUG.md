# Timezone Debug Guide for Remote Server

## Quick Fix Applied

✅ **Fixed the scheduler times** - Changed from 21:00/21:01 to 15:00/15:07 Moscow time

## Debugging Steps for Remote Server

### 1. Check Current Timezone Settings

```bash
# Run on your Digital Ocean droplet
python debug_timezone.py
```

This will show:
- Current system time (UTC and local)
- Configured timezone
- Next scheduled job times
- Time until next jobs

### 2. Test Scheduler Times

```bash
# Test the actual scheduler configuration
python test_scheduler_times.py
```

### 3. Check Container Timezone

```bash
# Check timezone inside Docker container
docker exec market_twits_app python debug_timezone.py
```

### 4. Verify Environment Variables

```bash
# Check if timezone is set correctly
docker exec market_twits_app env | grep SCHEDULER_TIMEZONE
```

## Expected Results

**Moscow Time (UTC+3):**
- News dump: 15:00 (3:00 PM)
- Summary push: 15:07 (3:07 PM)

**UTC Time:**
- News dump: 12:00 (12:00 PM)
- Summary push: 12:07 (12:07 PM)

## Common Issues & Solutions

### Issue 1: Wrong Timezone in Container
```bash
# Set timezone in docker-compose.yml
environment:
  - TZ=Europe/Moscow
  - SCHEDULER_TIMEZONE=Europe/Moscow
```

### Issue 2: System Timezone Mismatch
```bash
# Check system timezone
timedatectl

# Set system timezone (if needed)
sudo timedatectl set-timezone Europe/Moscow
```

### Issue 3: Container Not Using Correct Timezone
```bash
# Add to Dockerfile
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```

## Monitoring

### Check Scheduler Logs
```bash
# Watch scheduler logs
docker-compose logs -f app | grep -i scheduler
```

### Check Job Execution
```bash
# Check if jobs are running
docker-compose logs app | grep -i "daily.*job"
```

## Manual Test

To test if the scheduler is working, you can manually trigger a job:

```bash
# Test the standalone dumper
docker exec market_twits_app python standalone_dumper.py --daily
```

## Timezone Reference

| Location | Timezone | UTC Offset |
|----------|----------|------------|
| Moscow | Europe/Moscow | UTC+3 |
| UTC | UTC | UTC+0 |
| New York | America/New_York | UTC-5 (EST) |
| London | Europe/London | UTC+0 (GMT) |
