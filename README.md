# JetSet AI - AI-Powered Flight Search Assistant ✈️

A modern, full-stack web application that allows users to search for flights through natural language conversation with an AI-powered travel agent chatbot.

**🆕 Now powered by Claude Code CLI with real-time progress monitoring and MCP integration!**

![JetSet AI](frontend/src/assets/jetset-mascot.png)

## 🌟 Features

### Core Features
- **Natural Language Processing**: Ask for flights in plain English like "Find me a flight from NYC to London next Friday"
- **AI-Powered Search**: Powered by Claude Code CLI with access to real-time flight data via booking.com MCP integration
- **Conversational Interface**: Chat with JetSet, your friendly AI travel assistant
- **Modern UI/UX**: Clean, professional design with soft gradients, rounded corners, and smooth animations
- **Real-time Results**: Get instant flight recommendations with prices, durations, airlines, and layover information
- **Real-time Progress Monitoring**: See live updates as Claude Code searches for flights
- **Enhanced Loading Experience**: Progress bars, status messages, and travel tips while you wait

### 🆕 Advanced Conversation Features
- **Follow-up Questions**: Refine searches naturally - "no, next Wednesday" remembers your destination
- **Missing Information Handling**: Guides you through incomplete requests - asks for origin, destination, or date as needed
- **Date Range Clarification**: Understands "from March 1 to March 5" and asks if you want round-trip or flexible dates
- **Incremental Information Gathering**: Build your search across multiple messages naturally

### 🆕 Smart Date Parsing
- **Natural Language Dates**: "tomorrow", "this Friday", "next weekend", "next Monday"
- **15+ Date Formats**: Handles MM/DD/YYYY, DD/MM/YYYY, "March 15", and more
- **Smart Interpretation**: Distinguishes "this Friday" vs "next Friday" intelligently
- **Date Transparency**: Shows what date was understood - "on 2026-03-06 (you said: 'next Friday')"

### 🆕 Reliability & Performance
- **Fixed Script Architecture**: Consistent, reliable flight searches every time
- **Cross-Environment Compatibility**: Works in local dev, sandbox, and production without config changes
- **Fast Response Time**: File-based JSON approach eliminates 200-second waits
- **Robust Error Handling**: Friendly messages for invalid cities, no flights found, etc.

## 🎨 Design

- **Frontend**: React + TypeScript with Vite
- **Styling**: Tailwind CSS with custom gradient themes (purple-to-blue)
- **Backend**: Flask (Python) with Claude Code CLI integration
- **AI Engine**: Claude Code CLI with LiteLLM gateway
- **MCP Integration**: booking.com for real-time flight data
- **Monitoring**: Claude Monitor dashboard on port 9010
- **AI**: Claude AI (Opus 4.6 / Sonnet 4.6) via LiteLLM proxy
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

### Deployment

**🎉 No Configuration Needed!** The app automatically detects and adapts to different environments:

- ✅ **Auto-detects working directory**: Uses `/workspace` (sandbox) or local project root automatically
- ✅ **Auto-discovers MCP servers**: Finds the correct booking.com MCP server and tool prefix
- ✅ **Auto-retries tool calls**: Tries multiple tool name patterns if one fails

Simply deploy the code - it works in local development, sandbox, and production without changes!

#### Quick Start Scripts

**Production Mode** (Express server, port 3004):
```bash
./start.sh
```

**Development Mode** (Vite with hot reload, port 3002):
```bash
./start-dev.sh
```

See `Deploy dependencies.md` and `Deploy app.md` for detailed deployment instructions.

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

### Basic Searches
- "Find flights from Sydney to London next Friday"
- "Show me flights to Paris this weekend"
- "Direct flights to Tokyo tomorrow"
- "Cheapest flights to Miami next month"
- "Business class tickets to Dubai"

### Advanced Queries (New!)
- **Follow-ups**: "no, next Wednesday" (after initial search)
- **Date ranges**: "flights from Beijing to Singapore from March 1 to March 5"
- **Incomplete info**: "I want to go to Paris" → Bot asks for origin and date
- **Natural dates**: "this Friday", "next weekend", "tomorrow"

### Conversation Examples

**Example 1: Follow-up**
```
You: "flights from Beijing to Melbourne next Friday"
Bot: [Shows 8 flights]
You: "no, next Wednesday"
Bot: [Shows flights for Wednesday - remembered Beijing→Melbourne]
```

**Example 2: Date Range**
```
You: "flights from NYC to London from March 10 to March 15"
Bot: "Is this round-trip or flexible one-way dates?"
You: "round trip"
Bot: [Shows round-trip flights]
```

**Example 3: Incremental**
```
You: "I want to go to Paris"
Bot: "Where will you be flying from?"
You: "from New York"
Bot: "When would you like to travel?"
You: "next Friday"
Bot: [Shows flights NYC→Paris next Friday]
```

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

### Request Workflow (New Architecture)

When a user searches for flights, the following optimized sequence occurs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Flight Search Workflow (Optimized)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. [User] "flights from Beijing to Melbourne next Friday"                  │
│         ↓                                                                    │
│  2. [Sonnet 4.6] Extract parameters as JSON (FAST)                           │
│         → {origin: "Beijing", dest: "Melbourne", date: "next friday"}        │
│         ↓                                                                    │
│  3. [Backend] Validate parameters (origin, destination, date present?)      │
│         ├── Missing? → Ask user for missing info                             │
│         └── Complete? → Continue to search                                   │
│         ↓                                                                    │
│  4. [Fixed Script] flight_search.py executes:                                │
│         ├── Parse date: "next friday" → "2026-03-06"                         │
│         ├── Search destination: "Beijing" → PEK.AIRPORT                      │
│         ├── Search destination: "Melbourne" → MEL.CITY                       │
│         ├── Search flights: PEK → MEL on 2026-03-06                          │
│         ├── Process results (max 8 flights)                                  │
│         └── Save to /tmp/jetset_flights.json                                 │
│         ↓                                                                    │
│  5. [Backend] Read JSON file directly (FAST - no 200s wait)                 │
│         ↓                                                                    │
│  6. [Backend] Generate friendly response from template                      │
│         ↓                                                                    │
│  7. [Frontend] Render flight cards with booking links                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Improvements:**
- ✅ **Faster**: Claude only extracts parameters, not generates full scripts
- ✅ **Reliable**: Fixed script = consistent results every time
- ✅ **No 200s waits**: File-based JSON approach
- ✅ **Smart**: Handles follow-ups, missing info, date ranges

**Token Usage Example:**
| Step | Model/Process | Tokens/Time | Description |
|------|---------------|-------------|-------------|
| 2 | Sonnet 4.6 | ~5,000 tokens | Parameter extraction only |
| 3 | Backend logic | 0 tokens | Validation |
| 4 | flight_search.py | ~30 seconds | Booking.com API calls |
| 5-6 | Backend logic | 0 tokens | File read + template |
| **Total** | **Sonnet 4.6** | **~5,000 tokens** | **95% reduction!** |

### Frontend (React + TypeScript)
- **Components**:
  - `App.tsx` - Main application container
  - `ChatMessage.tsx` - Individual message bubbles
  - `ChatInput.tsx` - Message input field
  - `LoadingIndicator.tsx` - Loading animation
  - `Sidebar.tsx` - Navigation and features panel

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

