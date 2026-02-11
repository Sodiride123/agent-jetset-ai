# JetSet AI - AI-Powered Flight Search Assistant ✈️

A modern, full-stack web application that allows users to search for flights through natural language conversation with an AI-powered travel agent chatbot.

**🆕 Now powered by Claude Code CLI with real-time progress monitoring and MCP integration!**

![JetSet AI](frontend/src/assets/jetset-mascot.png)

## 🌟 Features

- **Natural Language Processing**: Ask for flights in plain English like "Find me a flight from NYC to London next Friday under $500"
- **AI-Powered Search**: Powered by Claude Code CLI with access to real-time flight data via booking.com MCP integration
- **Conversational Interface**: Chat with JetSet, your friendly AI travel assistant
- **Modern UI/UX**: Clean, professional design with soft gradients, rounded corners, and smooth animations
- **Real-time Results**: Get instant flight recommendations with prices, durations, airlines, and layover information
- **Context-Aware**: Refine searches with follow-up questions like "show me cheaper options" or "what about direct flights only?"
- **🆕 Real-time Progress Monitoring**: See live updates as Claude Code searches for flights
- **🆕 Enhanced Loading Experience**: Progress bars, status messages, and travel tips while you wait
- **🆕 Claude Monitor Dashboard**: Track token usage and performance metrics on port 9010

## 🎨 Design

- **Frontend**: React + TypeScript with Vite
- **Styling**: Tailwind CSS with custom gradient themes (purple-to-blue)
- **Backend**: Flask (Python) with Claude Code CLI integration
- **AI Engine**: Claude Code CLI with LiteLLM gateway
- **MCP Integration**: booking.com for real-time flight data
- **Monitoring**: Claude Monitor dashboard on port 9010
- **AI**: Claude AI (Opus 4.5) via LiteLLM proxy
- **Data**: booking.com MCP for real-time flight data

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm

### Backend Setup

1. Navigate to the backend directory:
```bash
cd jetset-ai/backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=your_base_url_here
ANTHROPIC_MODEL=your_model_here
FLASK_ENV=development
PORT=9002
```

5. Configure `settings.json` in the project root:
```json
{
    "env": {
        "ANTHROPIC_AUTH_TOKEN": "your_api_key_here",
        "ANTHROPIC_BASE_URL": "your_base_url_here",
        "ANTHROPIC_MODEL": "your_model_here"
    },
    "permissions": {
        "allow": ["Edit(**)", "Bash", "mcp__booking"]
    }
}
```

6. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:9002`

### Deployment Configuration

**Important:** When switching between local development and sandbox deployment, you need to update **2 files**:

#### 1. `backend/claude_wrapper.py` (Line ~44)

| Environment | Setting |
|-------------|---------|
| **Local Development** | `cwd=project_root` |
| **Company AI Sandbox** | `cwd='/workspace'` |

```python
# For local development:
cwd=project_root
#cwd='/workspace'

# For company AI sandbox deployment:
#cwd=project_root
cwd='/workspace'
```

#### 2. `backend/app.py` - System Prompt Paths (2 places, Lines ~57 and ~72)

| Environment | Path |
|-------------|------|
| **Local Development** | `cd /Users/yu.yan/code/agent-jetset-ai/backend && python3` |
| **Company AI Sandbox** | `cd /workspace/backend && python3` |

Search for `cd /Users/yu.yan/code/agent-jetset-ai/backend` and replace with `cd /workspace/backend` (or vice versa).

### MCP Configuration (for Local Development)

To use real flight data locally, you need to configure the booking.com MCP in your LiteLLM instance:

1. Access LiteLLM UI at `http://localhost:4000/ui`
2. Add a new MCP server with the following settings:

| Field | Value |
|-------|-------|
| Server Name | `booking_com_mcp` |
| Alias | `flights` |
| Server URL | `https://mcp.rapidapi.com` |
| Transport | `http` |
| Auth Type | `none` |

3. Add Static Headers:
   - `x-api-key`: Your RapidAPI key (get from https://rapidapi.com/tipsters/api/booking-com15)
   - `x-api-host`: `booking-com15.p.rapidapi.com`

4. Verify MCP is working:
```bash
curl -s -H "Authorization: Bearer YOUR_API_KEY" "http://localhost:4000/v1/mcp/server"
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd jetset-ai/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3002`

## 🌐 Live Demo

**Access the application at:** https://000ou.app.super.betamyninja.ai

## 📱 Usage

1. Open the application in your browser
2. Type your flight request in natural language, for example:
   - "I need a flight from New York to London next Friday for under $500"
   - "Show me weekend trips to Paris in March"
   - "Find direct flights to Tokyo departing next week"
3. JetSet will process your request and search for matching flights
4. Review the results and ask follow-up questions to refine your search
5. Click "New Chat" to start a fresh conversation

## 🎯 Example Queries

- "Find flights from NYC to London next Friday"
- "Show me weekend trips to Paris under $500"
- "Direct flights to Tokyo in March"
- "Cheapest flights to Miami next month"
- "Business class tickets to Dubai"

## 🏗️ Architecture

### Backend (Flask)
- **API Endpoints**:
  - `POST /api/chat` - Handle chat messages and flight searches
  - `POST /api/reset` - Reset conversation history
  - `GET /health` - Health check endpoint

- **AI Integration**:
  - Uses Claude AI via LiteLLM proxy
  - Integrates with booking.com MCP for flight data
  - Maintains conversation context for natural dialogue

### Request Workflow

When a user searches for flights, the following sequence occurs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Flight Search Workflow                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. [Sonnet 4.5] Initial warmup/loading                                      │
│         ↓                                                                    │
│  2. [Sonnet 4.5] Process user request, generate Python script                │
│         ↓                                                                    │
│  3. [Python Script] Execute booking.com API calls:                           │
│         ├── Search destination #1 (e.g., "Sydney" → SYD.AIRPORT)             │
│         ├── Search destination #2 (e.g., "Singapore" → SIN.CITY)             │
│         └── Search flights between destinations                              │
│         ↓                                                                    │
│  4. [Haiku 4.5] Internal processing (Claude Code CLI optimization)           │
│         ↓                                                                    │
│  5. [Sonnet 4.5] Generate final response with structured JSON                │
│         ↓                                                                    │
│  6. [Backend] Extract JSON from response, return to frontend                 │
│         ↓                                                                    │
│  7. [Frontend] Render flight cards with booking links                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Token Usage Example:**
| Step | Model | Tokens | Description |
|------|-------|--------|-------------|
| 1-2 | Sonnet 4.5 | ~18,000 | Initial request processing |
| 3 | python-requests | 0 | Booking.com API calls (3 requests) |
| 4 | Haiku 4.5 | ~7,000 | Internal optimization |
| 5 | Sonnet 4.5 | ~30,000 | Final response generation |

### Frontend (React + TypeScript)
- **Components**:
  - `App.tsx` - Main application container
  - `ChatMessage.tsx` - Individual message bubbles
  - `ChatInput.tsx` - Message input field
  - `LoadingIndicator.tsx` - Loading animation
  - `Sidebar.tsx` - Navigation and features panel

- **Styling**:
  - Tailwind CSS with custom configuration
  - Gradient backgrounds (purple-to-blue, teal-to-cyan)
  - Smooth animations and transitions
  - Responsive design

## 🎨 Design Philosophy

- **Clean & Modern**: Spacious layout with plenty of white space
- **Professional Yet Friendly**: Warm colors and approachable mascot
- **User-Centric**: Intuitive chat interface with clear visual hierarchy
- **Accessible**: High contrast, readable fonts, and clear CTAs

## 🔧 Technology Stack

- **Frontend**:
  - React 18
  - TypeScript
  - Vite
  - Tailwind CSS

- **Backend**:
  - Flask 3.0
  - Python 3.11
  - Anthropic Claude AI
  - booking.com MCP

- **Infrastructure**:
  - LiteLLM Proxy
  - CORS enabled
  - RESTful API

## 📝 API Documentation

### POST /api/chat

Send a message to the AI assistant.

**Request:**
```json
{
  "message": "Find flights from NYC to London",
  "conversation_id": "default"
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you find flights...",
  "conversation_id": "default",
  "tool_uses": [],
  "needs_continuation": false
}
```

### POST /api/reset

Reset the conversation history.

**Request:**
```json
{
  "conversation_id": "default"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation reset"
}
```

## 🤝 Contributing

This is a demonstration project showcasing AI-powered travel search capabilities.

## 📄 License

This project is created for demonstration purposes.

## 🙏 Acknowledgments

- Claude AI by Anthropic
- booking.com for flight data
- NinjaTech AI for the platform
- React and Vite communities
- Tailwind CSS team

## 📞 Support

For questions or issues, please refer to the documentation or contact support.

---

Built with ❤️ using Claude AI and modern web technologies
