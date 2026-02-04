# JetSet AI - Deployment Guide 🚀

## Current Deployment Status

✅ **Application is LIVE and Running!**

### Access Information

**🌐 Live Application URL:** https://000ou.app.super.betamyninja.ai

**📍 Local URLs:**
- Frontend: http://localhost:3000
- Backend: http://localhost:9000

### Service Status

| Service | Status | Port | URL |
|---------|--------|------|-----|
| Frontend (React) | ✅ Running | 3000 | https://000ou.app.super.betamyninja.ai |
| Backend (Flask) | ✅ Running | 9000 | http://localhost:9000 |
| Claude AI | ✅ Connected | - | Via LiteLLM Proxy |
| booking.com MCP | ✅ Available | - | Via Claude AI |

## Quick Start

### Option 1: Use Live Deployment
Simply visit: **https://000ou.app.super.betamyninja.ai**

### Option 2: Run Locally

1. **Start Backend:**
```bash
cd jetset-ai/backend
python app.py
```

2. **Start Frontend:**
```bash
cd jetset-ai/frontend
npm run dev
```

3. **Access Application:**
Open http://localhost:3000 in your browser

### Option 3: Use Start Script

```bash
cd jetset-ai
./start.sh
```

## Verification Steps

### 1. Check Backend Health

```bash
curl http://localhost:9000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-04T09:27:42.934780"
}
```

### 2. Test Chat API

```bash
curl -X POST http://localhost:9000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "test"}'
```

### 3. Access Frontend

Open browser and navigate to:
- Live: https://000ou.app.super.betamyninja.ai
- Local: http://localhost:3000

### 4. Test Full Flow

1. Open the application
2. Type: "Find flights from New York to London"
3. Wait for AI response
4. Verify flight search results appear

## Architecture Overview

```
┌──────────────────────────────────────┐
│         User's Browser               │
│  https://000ou.app.super.betamyninja │
└──────────────┬───────────────────────┘
               │
               │ HTTPS
               ▼
┌──────────────────────────────────────┐
│      React Frontend (Port 3000)      │
│  - Vite Dev Server                   │
│  - Tailwind CSS                      │
│  - TypeScript                        │
└──────────────┬───────────────────────┘
               │
               │ HTTP/REST API
               ▼
┌──────────────────────────────────────┐
│      Flask Backend (Port 9000)       │
│  - Python 3.11                       │
│  - CORS Enabled                      │
│  - Conversation Management           │
└──────────────┬───────────────────────┘
               │
               │ API Calls
               ▼
┌──────────────────────────────────────┐
│         LiteLLM Proxy                │
│  http://44.251.199.189:4000/         │
└──────────────┬───────────────────────┘
               │
               │ Claude AI API
               ▼
┌──────────────────────────────────────┐
│      Claude AI (Opus 4.5)            │
│  - Natural Language Processing       │
│  - booking.com MCP Integration       │
│  - Context Management                │
└──────────────┬───────────────────────┘
               │
               │ MCP Tools
               ▼
┌──────────────────────────────────────┐
│         booking.com API              │
│  - Flight Search                     │
│  - Real-time Data                    │
│  - Multiple Airlines                 │
└──────────────────────────────────────┘
```

## Environment Configuration

### Backend Environment (.env)

```bash
ANTHROPIC_API_KEY=sk-AL--pUYpwWLBvxV98Piucg
ANTHROPIC_BASE_URL=http://44.251.199.189:4000/
ANTHROPIC_MODEL=claude-opus-4-5-20251101
FLASK_ENV=development
PORT=9000
```

### Frontend Configuration (vite.config.ts)

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:9000',
        changeOrigin: true,
      }
    }
  }
})
```

## Port Configuration

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | React development server |
| Backend | 9000 | Flask API server |
| LiteLLM | 4000 | Claude AI proxy |
| Monitor | 9010 | Claude Code monitor dashboard |

## Monitoring & Logs

### Backend Logs

```bash
# View Flask logs
tail -f /workspace/outputs/workspace_output_*_9698.txt
```

### Frontend Logs

```bash
# View Vite logs
tail -f /workspace/outputs/workspace_output_*_5761.txt
```

### Claude Code Monitor

Access the monitoring dashboard at:
http://localhost:9010

This shows:
- Token usage
- API calls
- Performance metrics
- Error logs

## Troubleshooting

### Frontend Not Loading

1. Check if Vite is running:
```bash
ps aux | grep vite
```

2. Restart frontend:
```bash
cd jetset-ai/frontend
npm run dev
```

### Backend Not Responding

1. Check if Flask is running:
```bash
ps aux | grep python
```

2. Check health endpoint:
```bash
curl http://localhost:9000/health
```

3. Restart backend:
```bash
cd jetset-ai/backend
python app.py
```

### API Connection Issues

1. Verify CORS is enabled
2. Check network tab in browser DevTools
3. Verify backend URL in frontend code
4. Check firewall settings

### Claude AI Not Responding

1. Verify API key in .env
2. Check LiteLLM proxy status
3. Test direct API call:
```bash
curl -X POST http://44.251.199.189:4000/v1/messages \
  -H "Authorization: Bearer sk-AL--pUYpwWLBvxV98Piucg" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-opus-4-5-20251101", "max_tokens": 100, "messages": [{"role": "user", "content": "Hello"}]}'
```

## Performance Optimization

### Frontend

- **Build for Production:**
```bash
cd jetset-ai/frontend
npm run build
```

- **Preview Production Build:**
```bash
npm run preview
```

### Backend

- **Use Gunicorn (Production):**
```bash
cd jetset-ai/backend
gunicorn -w 4 -b 0.0.0.0:9000 app:app
```

## Security Considerations

### Current Setup (Development)

- ✅ CORS enabled for development
- ✅ Environment variables for secrets
- ✅ API key protection
- ⚠️ Debug mode enabled (development only)

### Production Recommendations

- [ ] Disable Flask debug mode
- [ ] Use HTTPS for all connections
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Use production WSGI server
- [ ] Set up proper CORS origins
- [ ] Implement request validation
- [ ] Add logging and monitoring
- [ ] Use database for conversations
- [ ] Implement session management

## Backup & Recovery

### Backup Conversation Data

Currently conversations are stored in memory. For production:

```python
# Add to backend
import json
import os

def backup_conversations():
    with open('conversations_backup.json', 'w') as f:
        json.dump(conversations, f)

def restore_conversations():
    if os.path.exists('conversations_backup.json'):
        with open('conversations_backup.json', 'r') as f:
            return json.load(f)
    return {}
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (Nginx, HAProxy)
- Deploy multiple backend instances
- Use Redis for shared conversation state
- Implement session affinity

### Vertical Scaling

- Increase server resources
- Optimize database queries
- Implement caching
- Use CDN for static assets

## Maintenance

### Regular Tasks

1. **Monitor Logs:**
   - Check for errors
   - Monitor API response times
   - Track usage patterns

2. **Update Dependencies:**
```bash
# Frontend
cd jetset-ai/frontend
npm update

# Backend
cd jetset-ai/backend
pip install --upgrade -r requirements.txt
```

3. **Backup Data:**
   - Export conversation logs
   - Save configuration files
   - Document changes

## Support Resources

### Documentation

- README.md - Main documentation
- QUICKSTART.md - Quick start guide
- FEATURES.md - Feature documentation
- PROJECT_SUMMARY.md - Project overview

### Monitoring

- Claude Code Monitor: http://localhost:9010
- Backend Health: http://localhost:9000/health
- Frontend: https://000ou.app.super.betamyninja.ai

### Logs

- Backend: `/workspace/outputs/workspace_output_*_9698.txt`
- Frontend: `/workspace/outputs/workspace_output_*_5761.txt`

---

## ✅ Deployment Checklist

- [x] Backend server running on port 9000
- [x] Frontend server running on port 3000
- [x] Port 3000 exposed to public internet
- [x] Health check endpoint responding
- [x] Claude AI integration working
- [x] booking.com MCP available
- [x] CORS configured correctly
- [x] Environment variables set
- [x] Mascot image loaded
- [x] Tailwind CSS configured
- [x] TypeScript compiled successfully
- [x] All components rendering
- [x] Chat functionality working
- [x] Error handling implemented
- [x] Documentation complete

## 🎉 Success!

**JetSet AI is successfully deployed and ready to use!**

Visit: **https://000ou.app.super.betamyninja.ai**

---

*Last Updated: February 4, 2026*