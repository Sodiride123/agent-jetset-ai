# JetSet AI - agents.rc Integration Guide

## Overview
This document describes the integration of JetSet AI with the agents.rc configuration, including Claude Code CLI, LiteLLM, and the booking.com MCP tool.

## Architecture Changes

### 1. Claude Code CLI Integration
- **Previous**: Direct API calls to Claude API
- **Current**: Uses Claude Code CLI with MCP tools enabled
- **Benefits**: 
  - Access to booking.com MCP for real-time flight data
  - Better tool orchestration
  - Automatic logging to `~/.claude/projects/jetset-ai`

### 2. LiteLLM Configuration
- **Endpoint**: `http://44.251.199.189:4000/`
- **API Key**: `sk-AL--pUYpwWLBvxV98Piucg`
- **Model**: `claude-opus-4-5-20251101`
- **Configuration File**: `~/.claude/settings.json`

### 3. MCP Integration
- **Service**: booking_com
- **Transport**: HTTP
- **Endpoint**: `http://44.251.199.189:4000/mcp`
- **Status**: ✓ Connected

## New Features

### 1. Progress Monitoring
**Backend Component**: `log_monitor.py`
- Monitors Claude Code logs in real-time
- Parses log entries for tool usage, MCP calls, and progress
- Provides status updates via `/api/progress` endpoint

**Frontend Component**: Enhanced `LoadingIndicator.tsx`
- Polls progress endpoint every 2 seconds
- Displays real-time status from Claude Code
- Shows progress bar based on actual processing state

### 2. Claude Monitor Dashboard
- **Port**: 9010
- **URL**: http://localhost:9010 (or https://000ti.app.super.betamyninja.ai)
- **Features**:
  - Token usage tracking
  - Request monitoring
  - Performance metrics
  - Real-time logs

### 3. Enhanced Error Handling
- Timeout management for long-running operations
- Automatic retry logic
- Graceful degradation when logs unavailable

## API Endpoints

### Existing Endpoints
- `GET /health` - Health check
- `POST /api/chat` - Send chat messages
- `POST /api/reset` - Reset conversation

### New Endpoints
- `GET /api/progress` - Get real-time progress updates
- `GET /api/monitor` - Get Claude Monitor dashboard info

## Testing

### Unit Tests
```bash
cd jetset-ai/backend
python -m unittest test_app.py -v
python -m unittest test_log_monitor.py -v
```

### Integration Tests
```bash
cd jetset-ai/backend
python -m unittest test_integration.py -v
```

### Test Coverage
- ✅ Health check endpoint
- ✅ Progress monitoring
- ✅ Chat endpoint (success/error cases)
- ✅ Conversation reset
- ✅ Log parsing
- ✅ Multiple conversations
- ✅ Error recovery

## Configuration Files

### 1. Claude Code Settings (`~/.claude/settings.json`)
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://44.251.199.189:4000/",
    "ANTHROPIC_AUTH_TOKEN": "sk-AL--pUYpwWLBvxV98Piucg",
    "ANTHROPIC_MODEL": "claude-opus-4-5-20251101"
  },
  "permissions": {
    "allow": [
      "Edit(**)",
      "Bash",
      "mcp__booking_com"
    ]
  }
}
```

### 2. Backend Environment (`.env`)
```env
ANTHROPIC_API_KEY=sk-AL--pUYpwWLBvxV98Piucg
ANTHROPIC_BASE_URL=http://44.251.199.189:4000/
ANTHROPIC_MODEL=claude-opus-4-5-20251101
FLASK_ENV=development
PORT=9002
```

## Deployment

### Services
1. **Backend (Flask)**: Port 9002
   ```bash
   cd jetset-ai/backend && python app.py
   ```

2. **Frontend (Express)**: Port 9000
   ```bash
   cd jetset-ai && node server.js
   ```

3. **Claude Monitor**: Port 9010
   - Automatically started by agents.rc script
   - Managed by systemd or runs as background process

### Public URLs
- **Application**: https://000tf.app.super.betamyninja.ai
- **Backend API**: http://localhost:9002
- **Claude Monitor**: https://000ti.app.super.betamyninja.ai

## Usage Examples

### 1. Basic Flight Search
```
User: "Find flights from New York to Miami tomorrow"
```

### 2. Progress Monitoring
```javascript
// Frontend polls this endpoint every 2 seconds
fetch('http://localhost:9002/api/progress')
  .then(res => res.json())
  .then(data => {
    console.log(data.status);    // 'processing', 'searching', etc.
    console.log(data.message);   // Human-readable status
    console.log(data.progress);  // 0-100
  });
```

### 3. Claude Monitor Access
```
Visit: http://localhost:9010
Or: https://000ti.app.super.betamyninja.ai
```

## Troubleshooting

### Issue: Progress endpoint returns idle status
**Solution**: Claude Code logs may not be created yet. Make a flight search request first.

### Issue: MCP connection failed
**Solution**: Verify MCP configuration:
```bash
claude mcp list
```

### Issue: Backend timeout
**Solution**: Claude Code CLI has 120-second timeout. For longer operations, the progress monitoring will show status updates.

### Issue: Frontend not showing progress
**Solution**: Check browser console for polling errors. Verify backend is running on port 9002.

## Performance Considerations

1. **Polling Interval**: 2 seconds (configurable in LoadingIndicator.tsx)
2. **CLI Timeout**: 120 seconds (configurable in claude_wrapper.py)
3. **Log Monitoring**: Minimal overhead, reads only new log entries
4. **Memory**: Conversation history limited to last 5 messages

## Security Notes

1. API keys are configured in environment variables
2. CORS enabled for development (restrict in production)
3. No sensitive data logged
4. MCP connection uses secure headers

## Future Enhancements

1. WebSocket support for real-time updates (eliminate polling)
2. Persistent conversation storage (database)
3. Advanced log analytics
4. Custom MCP tool development
5. Multi-user support with authentication

## References

- [Claude Code Documentation](https://code.claude.com/docs)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Booking.com API](https://www.booking.com/content/affiliates.html)