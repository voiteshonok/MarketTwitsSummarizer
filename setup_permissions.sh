#!/bin/bash
# Setup script for Digital Ocean droplet permissions

echo "Setting up permissions for MarketTwits Summarizer on Digital Ocean..."

# Create necessary directories if they don't exist
mkdir -p data logs

# Set proper ownership and permissions
echo "Setting ownership to UID 1000..."
sudo chown -R 1000:1000 data/ logs/

# Set proper permissions
echo "Setting directory permissions..."
chmod -R 755 data/ logs/

# Make sure the directories are writable
chmod -R 775 data/ logs/

echo "✅ Permissions set successfully!"
echo ""
echo "Directory structure:"
ls -la data/ logs/
echo ""
echo "You can now run: docker-compose up -d"
