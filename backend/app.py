from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import json
import logging
from datetime import datetime
from claude_wrapper import call_claude_with_mcp, reformat_to_structured_json
from log_monitor import ClaudeLogMonitor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# API Configuration
API_KEY = os.getenv('ANTHROPIC_API_KEY')
BASE_URL = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')
MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')

# Store conversation history (in production, use a database)
conversations = {}

# Initialize log monitor
log_monitor = ClaudeLogMonitor("jetset-ai")

SYSTEM_PROMPT = """You are JetSet, a friendly and professional AI travel agent assistant. You help users search for flights using natural language.

Your personality:
- Warm, friendly, and enthusiastic about travel
- Professional and knowledgeable
- Patient and helpful
- Use emojis occasionally to add personality (✈️, 🌍, 💼, etc.)

Your capabilities:
- You have access to the booking_com MCP tool to search for real flights
- You can understand natural language flight requests
- You extract: origin, destination, dates, number of passengers, class preferences, budget
- You provide flight recommendations with clear details

IMPORTANT: When returning flight search results, you MUST format your response as follows:

1. Start with a friendly conversational introduction
2. Then include a JSON block with structured flight data wrapped in ```json``` code blocks
3. End with helpful tips or follow-up suggestions

Example format:
```
Here are the flights I found for you! ✈️

```json
{
  "flights": [
    {
      "id": "1",
      "airline": "Air India",
      "flightNumber": "AI123",
      "price": 1037,
      "currency": "USD",
      "departure": {
        "time": "08:45",
        "date": "2026-02-05",
        "airport": "LHR",
        "city": "London"
      },
      "arrival": {
        "time": "19:15",
        "date": "2026-02-06",
        "airport": "SYD",
        "city": "Sydney"
      },
      "duration": "23h 30m",
      "stops": 1,
      "layovers": ["DXB"],
      "class": "Economy",
      "tags": ["cheapest"]
    }
  ],
  "summary": {
    "totalResults": 8,
    "cheapestPrice": 1037,
    "fastestDuration": "22h 50m",
    "averagePrice": 1200
  }
}
```

The cheapest option is Air India at $1,037, and the fastest is Cathay Pacific at 22h 50m. Would you like more details on any of these flights?
```

Always include both the conversational text AND the structured JSON data for flight results!"""

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and flight searches"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        
        logger.info(f"Received message: {user_message[:100]}...")
        
        # Initialize conversation history if needed
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add user message to history
        conversations[conversation_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Step 1: Call Claude Code CLI with MCP tools to get flight data
        logger.info("Step 1: Calling Claude Code CLI with MCP tools...")
        
        result = call_claude_with_mcp(user_message, conversations[conversation_id][:-1])
        
        if not result['success']:
            raise Exception(result['error'] or 'Failed to get response from Claude')
        
        assistant_message = result['response']
        
        # Step 2: Reformat the response into structured JSON
        logger.info("Step 2: Reformatting response into structured JSON...")
        flight_data = reformat_to_structured_json(assistant_message, user_message)
        
        # Add assistant response to history
        conversations[conversation_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        logger.info(f"Sending response: {assistant_message[:100]}...")
        
        return jsonify({
            'response': assistant_message,
            'conversation_id': conversation_id,
            'flight_data': flight_data,
            'tool_uses': [],
            'needs_continuation': False
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred processing your request',
            'details': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation history"""
    try:
        data = request.json
        conversation_id = data.get('conversation_id', 'default')
        
        if conversation_id in conversations:
            del conversations[conversation_id]
        
        return jsonify({'status': 'success', 'message': 'Conversation reset'})
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get current processing progress from Claude Code logs"""
    try:
        status = log_monitor.get_current_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error monitoring progress',
            'progress': 0
        }), 500

@app.route('/api/monitor', methods=['GET'])
def monitor_dashboard():
    """Redirect to Claude Monitor dashboard"""
    return jsonify({
        'dashboard_url': 'http://localhost:9010',
        'message': 'Claude Code monitoring dashboard is available at port 9010'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 9000))
    logger.info(f"Starting JetSet AI backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
