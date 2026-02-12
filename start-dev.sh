#!/bin/bash

echo "🚀 Starting JetSet AI Application (Development Mode)..."
echo ""

# Cleanup function for Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Check for local .env file
if [ -f "backend/.env" ]; then
    echo "✅ Using existing backend/.env"
else
    echo "⚠️  Warning: backend/.env not found"
    echo "Please create backend/.env with your API credentials"
fi

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

# Start Vite dev server
echo "🎨 Starting Vite dev server on port 3002..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ JetSet AI is now running (Development Mode)!"
echo ""
echo "📍 Frontend: http://localhost:3002  ← Open this in browser"
echo "📍 Backend:  http://localhost:9002"
echo ""
echo "💡 Hot reload enabled - changes update instantly!"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
