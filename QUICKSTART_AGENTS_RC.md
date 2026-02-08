# JetSet AI - Quick Start Guide (agents.rc Configuration)

## Prerequisites
- agents.rc script has been run successfully
- Claude Code CLI is installed and configured
- booking.com MCP is connected

## Verify Installation

### 1. Check Claude Code Configuration
```bash
cat ~/.claude/settings.json
```
Should show LiteLLM endpoint: `http://44.251.199.189:4000/`

### 2. Verify MCP Connection
```bash
claude mcp list
```
Should show: `booking_com: http://44.251.199.189:4000/mcp (HTTP) - ✓ Connected`

### 3. Check Services
```bash
netstat -tlnp | grep -E "(9000|9002|9010)"
```
Should show three services running on ports 9000, 9002, and 9010.

## Starting the Application

### Option 1: All Services (Recommended)
```bash
cd /workspace/jetset-ai

# Start backend
cd backend && python app.py &

# Start frontend
cd .. && node server.js &
```

### Option 2: Individual Services

**Backend Only:**
```bash
cd /workspace/jetset-ai/backend
python app.py
```

**Frontend Only:**
```bash
cd /workspace/jetset-ai
node server.js
```

**Claude Monitor** (automatically started by agents.rc):
- Already running on port 9010
- Access at: http://localhost:9010

## Accessing the Application

### Local Access
- **Main Application**: http://localhost:9000
- **Backend API**: http://localhost:9002
- **Claude Monitor**: http://localhost:9010

### Public Access (if ports exposed)
- **Main Application**: https://000tf.app.super.betamyninja.ai
- **Claude Monitor**: https://000ti.app.super.betamyninja.ai

## Testing the Application

### 1. Health Check
```bash
curl http://localhost:9002/health
```
Expected response:
```json
{"status": "healthy", "timestamp": "2024-02-08T19:00:00.000000"}
```

### 2. Progress Endpoint
```bash
curl http://localhost:9002/api/progress
```
Expected response:
```json
{"status": "idle", "message": "Waiting for activity...", "progress": 0}
```

### 3. Test Flight Search
Open http://localhost:9000 in your browser and try:
```
Find flights from New York to Miami tomorrow
```

### 4. Monitor Dashboard
Open http://localhost:9010 to see:
- Token usage
- Request logs
- Performance metrics

## Running Tests

### Unit Tests
```bash
cd /workspace/jetset-ai/backend

# Test backend
python -m unittest test_app.py -v

# Test log monitor
python -m unittest test_log_monitor.py -v
```

### Integration Tests
```bash
cd /workspace/jetset-ai/backend
python -m unittest test_integration.py -v
```

### Expected Results
All tests should pass:
- 7 unit tests for backend
- 8 unit tests for log monitor
- 4 integration tests

## Troubleshooting

### Backend won't start
```bash
# Check if port is in use
lsof -ti:9002 | xargs kill -9

# Restart backend
cd /workspace/jetset-ai/backend && python app.py
```

### Frontend won't start
```bash
# Check if port is in use
lsof -ti:9000 | xargs kill -9

# Restart frontend
cd /workspace/jetset-ai && node server.js
```

### Claude Code not responding
```bash
# Verify configuration
cat ~/.claude/settings.json

# Test Claude Code directly
claude -p "Hello, test message"
```

### MCP connection issues
```bash
# Check MCP status
claude mcp list

# If not connected, re-add
claude mcp add --scope user --transport http booking_com \
  "http://44.251.199.189:4000/mcp" \
  --header "x-litellm-api-key: Bearer sk-AL--pUYpwWLBvxV98Piucg"
```

### Progress monitoring not working
```bash
# Check if logs directory exists
ls -la ~/.claude/projects/jetset-ai

# If not, make a test query first to create logs
```

## Key Features to Test

1. **Natural Language Search**
   - "Find flights from NYC to LAX tomorrow"
   - "Show me cheap flights to Paris next week"
   - "I need a direct flight to London under $500"

2. **Progress Monitoring**
   - Watch the loading indicator show real-time status
   - See progress bar advance as search progresses
   - View travel tips while waiting

3. **Claude Monitor**
   - Check token usage after searches
   - View request logs
   - Monitor performance metrics

4. **Conversation Context**
   - Ask follow-up questions
   - Refine search criteria
   - Request different options

## Performance Expectations

- **Initial Load**: < 2 seconds
- **Flight Search**: 30-60 seconds (with real-time progress)
- **Progress Updates**: Every 2 seconds
- **API Response**: < 100ms (health/progress endpoints)

## Next Steps

1. Try different flight search queries
2. Monitor token usage in Claude Monitor dashboard
3. Review logs in `~/.claude/projects/jetset-ai`
4. Experiment with conversation context
5. Test error handling with invalid queries

## Support

For issues or questions:
1. Check logs: `~/.claude/projects/jetset-ai/*.log`
2. Review backend logs: Check terminal output
3. Inspect browser console: F12 in browser
4. Consult: `AGENTS_RC_INTEGRATION.md` for detailed documentation

## Advanced Usage

### Custom Configuration
Edit `~/.claude/settings.json` to:
- Change model
- Adjust permissions
- Modify environment variables

### Development Mode
```bash
# Backend with auto-reload
cd /workspace/jetset-ai/backend
FLASK_ENV=development python app.py

# Frontend with hot reload
cd /workspace/jetset-ai/frontend
npm run dev
```

### Production Deployment
See `DEPLOYMENT.md` for production setup instructions.