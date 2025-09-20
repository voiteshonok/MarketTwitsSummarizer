# Digital Ocean Deployment Guide

## Quick Fix for Permission Issues

### Option 1: Manual Permission Setup (Recommended)

1. **Run the setup script:**
   ```bash
   ./setup_permissions.sh
   ```

2. **Start the services:**
   ```bash
   docker-compose up -d
   ```

### Option 2: Using Init Container

If the manual setup doesn't work, use the init container approach:

```bash
docker-compose -f docker-compose.init.yml up -d
```

### Option 3: Manual Commands

If you prefer to run commands manually:

```bash
# Create directories
mkdir -p data logs

# Set ownership (replace 'ubuntu' with your username if different)
sudo chown -R 1000:1000 data/ logs/

# Set permissions
chmod -R 755 data/ logs/

# Make writable
chmod -R 775 data/ logs/

# Start services
docker-compose up -d
```

## Troubleshooting

### Check Container Logs
```bash
docker-compose logs app
```

### Check Directory Permissions
```bash
ls -la data/ logs/
```

### Fix Permission Issues
```bash
# Stop containers
docker-compose down

# Fix permissions
sudo chown -R 1000:1000 data/ logs/
chmod -R 775 data/ logs/

# Restart
docker-compose up -d
```

### Verify Everything Works
```bash
# Check health
curl http://localhost:8000/health

# Check logs are being written
tail -f logs/market_twits.log
```

## Common Issues

1. **Permission Denied**: Run the setup script or manual permission commands
2. **Container Won't Start**: Check logs with `docker-compose logs app`
3. **Redis Connection Issues**: Ensure Redis container is running with `docker-compose ps`

## Production Considerations

- Consider using Docker secrets for sensitive data
- Set up log rotation for the logs directory
- Monitor disk space usage
- Set up proper backup for the data directory
