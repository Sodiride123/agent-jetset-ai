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

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=your_base_url_here
ANTHROPIC_MODEL=your_model_here
FLASK_ENV=development
PORT=9002
```

4. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:9000`

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

The frontend will run on `http://localhost:3000`

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
