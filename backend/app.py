from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
from dotenv import load_dotenv
import requests
import json
import logging
import re
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
MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-opus-4-6')

# Store conversation history (in production, use a database)
conversations = {}

# Initialize log monitor
log_monitor = ClaudeLogMonitor("jetset-ai")

# SYSTEM PROMPT FOR PARAMETER EXTRACTION
# Claude only extracts search parameters - the fixed script handles the actual search
SYSTEM_PROMPT = """You are JetSet, a friendly AI travel assistant. Your job is to understand user travel requests and extract search parameters.

IMPORTANT: You have access to the CONVERSATION HISTORY. Use it to understand follow-up questions!

IMPORTANT: You MUST respond with a JSON object for travel-related requests. Do NOT run any Python code or scripts.

For FLIGHT searches, respond with ONLY this JSON format:
```json
{
    "type": "flight_search",
    "origin": "city or airport name",
    "destination": "city or airport name",
    "date": "the departure date in any format",
    "adults": 1,
    "cabin_class": "ECONOMY",
    "return_date": null
}
```

For GENERAL CONVERSATION (greetings, questions, etc.), respond with:
```json
{
    "type": "conversation",
    "response": "Your friendly response here"
}
```

RULES:
1. Extract the origin and destination cities/airports from the user's message
2. Extract the date - keep it as the user said it (e.g., "next friday", "March 15", "tomorrow")
3. Default adults to 1 unless specified
4. Default cabin_class to "ECONOMY" unless user mentions business/first class
5. Set return_date only for round trips
6. For greetings or non-search messages, use type "conversation"

HANDLING FOLLOW-UP QUESTIONS:
- If the user says something like "no, next Wednesday" or "change to Thursday", look at the PREVIOUS messages to find the origin and destination, then use the NEW date
- If the user says "what about to Singapore instead", keep the same origin and date but change the destination
- If the user provides a completely new search like "now check Beijing to Tokyo on March 5", treat it as a fresh search
- ALWAYS try to understand the user's intent from context

EXAMPLES:

User: "Find me a flight from Beijing to Melbourne next Friday"
```json
{
    "type": "flight_search",
    "origin": "Beijing",
    "destination": "Melbourne",
    "date": "next friday",
    "adults": 1,
    "cabin_class": "ECONOMY",
    "return_date": null
}
```

[Previous search was: Beijing to Melbourne next Friday]
User: "no, next Wednesday"
```json
{
    "type": "flight_search",
    "origin": "Beijing",
    "destination": "Melbourne",
    "date": "next wednesday",
    "adults": 1,
    "cabin_class": "ECONOMY",
    "return_date": null
}
```

[Previous search was: Beijing to Melbourne]
User: "what about Singapore instead"
```json
{
    "type": "flight_search",
    "origin": "Beijing",
    "destination": "Singapore",
    "date": "next friday",
    "adults": 1,
    "cabin_class": "ECONOMY",
    "return_date": null
}
```

User: "I need 2 business class tickets from NYC to London on March 15th"
```json
{
    "type": "flight_search",
    "origin": "New York",
    "destination": "London",
    "date": "March 15",
    "adults": 2,
    "cabin_class": "BUSINESS",
    "return_date": null
}
```

User: "Hello!"
```json
{
    "type": "conversation",
    "response": "Hello! ✈️ Welcome to JetSet! I'm here to help you find the best flights. Just tell me where you'd like to go and when, and I'll search for options!"
}
```

User: "Thanks for your help!"
```json
{
    "type": "conversation",
    "response": "You're welcome! ✈️ Have a wonderful trip! Feel free to come back anytime you need help finding flights. Safe travels! 🌍"
}
```

RESPOND WITH ONLY THE JSON OBJECT - NO OTHER TEXT."""


def run_flight_search(params: dict) -> dict:
    """Run the fixed flight_search.py script with extracted parameters."""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flight_search.py')

        cmd = [
            'python3', script_path,
            '--origin', params.get('origin', ''),
            '--destination', params.get('destination', ''),
            '--date', params.get('date', 'next week'),
            '--adults', str(params.get('adults', 1)),
            '--cabin_class', params.get('cabin_class', 'ECONOMY').upper()
        ]

        if params.get('return_date'):
            cmd.extend(['--return_date', params['return_date']])

        logger.info(f"Running flight search: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        logger.info(f"Flight search stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Flight search stderr: {result.stderr}")

        # Read results from file
        output_file = '/tmp/jetset_flights.json'
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                return json.load(f)

        return {"error": "No results file found", "flights": [], "summary": {}}

    except subprocess.TimeoutExpired:
        logger.error("Flight search timeout")
        return {"error": "Search timeout", "flights": [], "summary": {}}
    except Exception as e:
        logger.error(f"Flight search error: {str(e)}")
        return {"error": str(e), "flights": [], "summary": {}}


def generate_flight_response(flight_data: dict, params: dict) -> str:
    """Generate a friendly response from flight search results."""
    flights = flight_data.get('flights', [])
    summary = flight_data.get('summary', {})
    error = flight_data.get('error')

    origin = summary.get('origin', params.get('origin', 'Origin'))
    destination = summary.get('destination', params.get('destination', 'Destination'))
    date = summary.get('date', params.get('date', ''))

    if error:
        return f"""😔 Sorry, I encountered an issue while searching for flights.

**Error:** {error}

💡 **Suggestions:**
- Check if the city names are spelled correctly
- Try using airport codes (e.g., "JFK" instead of "New York")
- Make sure the date is valid

Would you like to try a different search?"""

    if not flights:
        return f"""😔 No flights found from {origin} to {destination} on {date}.

This could be because:
- The date might be too far in the future or past
- No airlines operate this route on that day
- All flights are sold out

💡 **Suggestions:**
- Try a different date (±1-2 days)
- Try nearby airports
- Check for connecting flights

Would you like me to search for a different date or route?"""

    # Find cheapest and fastest flights
    cheapest = min(flights, key=lambda f: f.get('price', float('inf')))
    fastest = min(flights, key=lambda f: _duration_to_minutes(f.get('duration', '999h')))

    # Find a budget alternative (different from cheapest)
    budget = None
    for f in flights:
        if f['id'] != cheapest['id'] and f['id'] != fastest['id']:
            budget = f
            break

    currency = flights[0].get('currency', 'USD')

    response = f"""✈️ Found **{len(flights)} flights** from {origin} to {destination} on {date}!

💰 **Best Value:** {cheapest['airline']} - ${cheapest['price']} {currency} ({_stops_text(cheapest['stops'])}, {cheapest['duration']})
⚡ **Fastest:** {fastest['airline']} - ${fastest['price']} {currency} ({_stops_text(fastest['stops'])}, {fastest['duration']})"""

    if budget:
        response += f"""
💵 **Alternative:** {budget['airline']} - ${budget['price']} {currency} ({_stops_text(budget['stops'])}, {budget['duration']})"""

    price_range = f"${summary.get('cheapestPrice', cheapest['price'])} - ${max(f['price'] for f in flights)}"
    dep_code = flights[0].get('departure', {}).get('airport', '')
    arr_code = flights[0].get('arrival', {}).get('airport', '')

    response += f"""

📊 **Price Range:** {price_range} {currency}
🛫 **Route:** {dep_code} → {arr_code}

Click on any flight card below to book directly! ✨"""

    return response


def _duration_to_minutes(duration: str) -> int:
    """Convert duration string like '12h 30m' to minutes."""
    try:
        match = re.match(r'(\d+)h\s*(\d+)?m?', duration)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2) or 0)
            return hours * 60 + minutes
    except:
        pass
    return 9999


def _stops_text(stops: int) -> str:
    """Convert stops count to text."""
    if stops == 0:
        return "direct"
    elif stops == 1:
        return "1 stop"
    else:
        return f"{stops} stops"

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

        # Step 1: Call Claude to extract parameters (fast, no script generation)
        logger.info("Step 1: Extracting search parameters with Claude...")

        result = call_claude_with_mcp(user_message, conversations[conversation_id][:-1], system_prompt=SYSTEM_PROMPT)

        if not result['success']:
            raise Exception(result['error'] or 'Failed to get response from Claude')

        raw_response = result['response']
        logger.info(f"Claude response: {raw_response[:200]}...")

        # Step 2: Parse the JSON parameters from Claude's response
        logger.info("Step 2: Parsing parameters...")

        params = None

        # Try multiple patterns to extract JSON
        # Pattern 1: JSON in markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
        if json_match:
            try:
                params = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Pattern 2: Raw JSON with "type" key
        if not params:
            json_match = re.search(r'(\{[^{}]*"type"\s*:\s*"[^"]+"\s*[^{}]*\})', raw_response, re.DOTALL)
            if json_match:
                try:
                    params = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

        # Pattern 3: More flexible JSON extraction
        if not params:
            json_match = re.search(r'\{.*"type".*\}', raw_response, re.DOTALL)
            if json_match:
                try:
                    # Clean up the JSON string
                    json_str = json_match.group(0)
                    # Fix common issues
                    json_str = re.sub(r'[\x00-\x1f]', ' ', json_str)  # Remove control characters
                    params = json.loads(json_str)
                except json.JSONDecodeError:
                    pass

        # Fallback: treat as conversation
        if not params:
            logger.warning(f"Could not parse JSON from response, treating as conversation")
            params = {"type": "conversation", "response": raw_response}

        logger.info(f"Parsed params: {params}")

        # Step 3: Handle based on request type
        flight_data = None
        assistant_message = ""

        if params.get('type') == 'flight_search':
            # Run the fixed flight search script
            logger.info("Step 3: Running fixed flight search script...")
            flight_data = run_flight_search(params)

            # Generate friendly response from results
            logger.info("Step 4: Generating response...")
            assistant_message = generate_flight_response(flight_data, params)

        elif params.get('type') == 'conversation':
            # Just return the conversation response
            assistant_message = params.get('response', "Hello! How can I help you find flights today?")

        else:
            # Unknown type, return raw response
            assistant_message = raw_response

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
    port = int(os.getenv('PORT', 9002))
    logger.info(f"Starting JetSet AI backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
