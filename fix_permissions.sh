#!/bin/bash
# Quick fix for permission issues on Digital Ocean

echo "🔧 Fixing permissions for MarketTwits Summarizer..."

# Stop containers if running
echo "Stopping containers..."
docker-compose down

# Create directories if they don't exist
echo "Creating directories..."
mkdir -p data logs

# Set ownership to UID 1000
echo "Setting ownership to UID 1000:1000..."
sudo chown -R 1000:1000 data/ logs/

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 data/ logs/

# Make writable
echo "Making directories writable..."
chmod -R 775 data/ logs/

# Verify permissions
echo ""
echo "✅ Permissions set! Current status:"
ls -la data/ logs/

echo ""
echo "You can now run: docker-compose up -d"
