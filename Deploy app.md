# Deploy App

This guide configures API keys and starts the JetSet AI application on a pre-installed VM.

## Prerequisites

- VM with dependencies pre-installed (see `Deploy dependencies.md`)
- API credentials available in `/root/.claude/settings.json`

## Quick Start

Just run the start script - it handles everything automatically:

```bash
cd /workspace/agent-jetset-ai

# Make start script executable (if not already)
chmod +x start.sh

# Run the start script
./start.sh
```

The script will:
1. Extract credentials from `/root/.claude/settings.json`
2. Update `backend/.env` with API credentials
3. Update `settings.json` with Claude CLI credentials
4. Activate Python virtual environment
5. Start the Flask backend on port 9002
6. Start the React frontend on port 3002

Press `Ctrl+C` to stop all services (cleanup is handled automatically).

## Manual Configuration (Alternative)

If credentials are not available in `/root/.claude/settings.json`, configure manually:

### Step 1: Configure Backend Environment

```bash
cd /workspace/agent-jetset-ai/backend

# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=your_base_url_here
ANTHROPIC_MODEL=your_model_here
FLASK_ENV=development
PORT=9002
EOF
```

### Step 2: Configure Claude CLI Settings

```bash
cd /workspace/agent-jetset-ai

# Edit settings.json
cat > settings.json << EOF
{
    "env": {
        "ANTHROPIC_AUTH_TOKEN": "your_api_key_here",
        "ANTHROPIC_BASE_URL": "your_base_url_here",
        "ANTHROPIC_MODEL": "your_model_here"
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
```

### Step 3: Start Backend

```bash
cd /workspace/agent-jetset-ai/backend

# Activate virtual environment
source .venv/bin/activate

# Start Flask server
python app.py &
```

### Step 4: Start Frontend

```bash
cd /workspace/agent-jetset-ai/frontend

# Start development server
npm run dev &
```

## Verify Application is Running

```bash
# Check backend health
curl http://localhost:9002/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

Access the application:
- **Frontend:** http://localhost:3002
- **Backend API:** http://localhost:9002

## Stop the Application

```bash
# Find and kill processes
pkill -f "python app.py"
pkill -f "npm run dev"

# Or if started with start.sh, press Ctrl+C
```

## Troubleshooting

### Backend not starting
```bash
# Check if port 9002 is in use
lsof -i :9002

# Check backend logs
cd /workspace/agent-jetset-ai/backend
source .venv/bin/activate
python app.py
```

### Frontend not starting
```bash
# Check if port 3002 is in use
lsof -i :3002

# Check frontend logs
cd /workspace/agent-jetset-ai/frontend
npm run dev
```

### API errors
- Verify `ANTHROPIC_API_KEY` is correct in `backend/.env`
- Verify `ANTHROPIC_AUTH_TOKEN` is correct in `settings.json`
- Check that `ANTHROPIC_BASE_URL` is accessible from the VM
