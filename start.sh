#!/bin/bash

echo "🚀 Starting JetSet AI Application..."
echo ""

# Extract credentials from Claude settings
echo "🔑 Extracting credentials from Claude settings..."
CLAUDE_SETTINGS="/root/.claude/settings.json"

if [ -f "$CLAUDE_SETTINGS" ]; then
    # Extract API key and base URL using jq
    ANTHROPIC_API_KEY=$(jq -r '.env.ANTHROPIC_AUTH_TOKEN' "$CLAUDE_SETTINGS")
    ANTHROPIC_BASE_URL=$(jq -r '.env.ANTHROPIC_BASE_URL' "$CLAUDE_SETTINGS")
    ANTHROPIC_MODEL=$(jq -r '.env.ANTHROPIC_MODEL' "$CLAUDE_SETTINGS")
    
    # Update backend/.env file
    echo "📝 Updating backend/.env with credentials..."
    cat > backend/.env << EOF
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL
ANTHROPIC_MODEL=$ANTHROPIC_MODEL
FLASK_ENV=development
PORT=9002
EOF
    echo "✅ Credentials updated successfully"
else
    echo "⚠️  Warning: Claude settings file not found at $CLAUDE_SETTINGS"
    echo "Using existing .env file..."
fi

echo ""

# Start backend
echo "📦 Starting Flask backend on port 9002..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting React frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ JetSet AI is now running!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend:  http://localhost:9000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
