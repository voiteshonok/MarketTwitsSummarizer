#!/bin/bash
# Deployment script for Digital Ocean droplet

set -e  # Exit on error

echo "🚀 Deploying MarketTwits Summarizer on Digital Ocean"
echo "=" * 60

# Step 1: Create directories
echo ""
echo "📁 Step 1: Creating directories..."
mkdir -p data logs
echo "✅ Directories created"

# Step 2: Set ownership
echo ""
echo "👤 Step 2: Setting ownership..."
if [ "$EUID" -eq 0 ]; then
    # Running as root
    chown -R 1000:1000 data/ logs/
else
    # Not root, use sudo
    sudo chown -R 1000:1000 data/ logs/
fi
echo "✅ Ownership set to 1000:1000"

# Step 3: Set permissions
echo ""
echo "🔐 Step 3: Setting permissions..."
chmod -R 755 data/ logs/
chmod -R 775 data/ logs/
echo "✅ Permissions set"

# Step 4: Verify .env file exists
echo ""
echo "📝 Step 4: Checking .env file..."
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from env.example..."
    cp env.example .env
    echo "❗ Please edit .env file with your credentials before proceeding!"
    echo "   Especially set: TELEGRAM_SESSION_STRING"
    exit 1
fi

# Check if SESSION_STRING is set
if ! grep -q "^TELEGRAM_SESSION_STRING=.\+" .env; then
    echo "⚠️  Warning: TELEGRAM_SESSION_STRING not set in .env!"
    echo "Please run: python generate_session_string.py"
    echo "And add the output to your .env file"
    exit 1
fi

echo "✅ .env file configured"

# Step 5: Pull/Build images
echo ""
echo "🐳 Step 5: Building Docker images..."
docker-compose build --no-cache

echo "✅ Docker images built"

# Step 6: Start services
echo ""
echo "🚀 Step 6: Starting services..."
docker-compose up -d

echo "✅ Services started"

# Step 7: Wait for health check
echo ""
echo "⏳ Step 7: Waiting for application to be healthy..."
sleep 10

# Check if containers are running
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ Application is healthy!"
elif docker-compose ps | grep -q "Up (health: starting)"; then
    echo "⏳ Application is starting, health check pending..."
else
    echo "❌ Application may have issues. Check logs:"
    echo "   docker-compose logs app"
    exit 1
fi

# Step 8: Show status
echo ""
echo "📊 Step 8: Service status"
docker-compose ps

# Step 9: Verify
echo ""
echo "🧪 Step 9: Running verification tests..."

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Health endpoint responding"
else
    echo "⚠️  Health endpoint not responding yet"
fi

# Step 10: Show logs
echo ""
echo "📋 Recent logs:"
docker-compose logs app --tail=20

echo ""
echo "=" * 60
echo "✅ Deployment complete!"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f app"
echo "  - Check status: docker-compose ps"
echo "  - Restart: docker-compose restart app"
echo "  - Stop: docker-compose down"
echo "  - Rebuild: docker-compose build --no-cache app"
echo ""
echo "API is available at: http://your-droplet-ip:8000"
echo "Documentation: http://your-droplet-ip:8000/docs"
