#!/bin/bash

echo "🚀 Starting JetSet AI Application (Production Mode)..."
echo ""

# Extract credentials from Claude settings
echo "🔑 Extracting credentials from Claude settings..."
CLAUDE_SETTINGS="/root/.claude/settings.json"

if [ -f "$CLAUDE_SETTINGS" ]; then
    # Extract API key and base URL using jq
    ANTHROPIC_API_KEY=$(jq -r '.env.ANTHROPIC_AUTH_TOKEN' "$CLAUDE_SETTINGS")
    ANTHROPIC_BASE_URL=$(jq -r '.env.ANTHROPIC_BASE_URL' "$CLAUDE_SETTINGS")
    ANTHROPIC_MODEL=claude-opus-4-6

    # Update backend/.env file
    echo "📝 Updating backend/.env with credentials..."
    cat > backend/.env << EOF
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL
ANTHROPIC_MODEL=$ANTHROPIC_MODEL
ANTHROPIC_DEFAULT_HAIKU_MODEL=$ANTHROPIC_MODEL
ANTHROPIC_DEFAULT_SONNET_MODEL=$ANTHROPIC_MODEL
ANTHROPIC_DEFAULT_OPUS_MODEL=$ANTHROPIC_MODEL
FLASK_ENV=development
PORT=9002
EOF

    # Update settings.json with credentials for Claude CLI
    echo "📝 Updating settings.json with credentials..."
    cat > settings.json << EOF
{
    "env": {
        "ANTHROPIC_AUTH_TOKEN": "$ANTHROPIC_API_KEY",
        "ANTHROPIC_BASE_URL": "$ANTHROPIC_BASE_URL",
        "ANTHROPIC_MODEL": "$ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "$ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "$ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "$ANTHROPIC_MODEL"
    },
    "permissions": {
        "allow": [
            "Edit(**)",
            "Bash",
            "mcp__booking"
        ]
    }
}
EOF

    echo "✅ Credentials updated successfully"
else
    echo "⚠️  Warning: Claude settings file not found at $CLAUDE_SETTINGS"
    echo "Using existing .env file..."
fi

echo ""

# Build frontend for production
echo "🔨 Building frontend for production..."
cd frontend
npm run build
cd ..
echo "✅ Frontend build complete"

echo ""

# Start backend
echo "📦 Starting Flask backend on port 9002..."
cd backend
source .venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Express server (serves production build + proxies API)
echo "🌐 Starting Express server on port 3004..."
node server.js &
FRONTEND_PID=$!

echo ""
echo "✅ JetSet AI is now running (Production Mode)!"
echo ""
echo "📍 App URL:  http://localhost:3004  ← Expose this port to CloudFront"
echo "📍 Backend:  http://localhost:9002  (internal)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
