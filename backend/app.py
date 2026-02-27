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
# Store last search parameters per conversation for better context
last_search_params = {}

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

For DATE RANGE CLARIFICATION (when user provides a date range), respond with:
```json
{
    "type": "date_range_clarification",
    "origin": "city name",
    "destination": "city name",
    "date_range_start": "start date",
    "date_range_end": "end date",
    "response": "Ask user if they have a specific date or want to see all flights in the range"
}
```

For GENERAL CONVERSATION (greetings, questions, etc.), respond with:
```json
{
    "type": "conversation",
    "response": "Your friendly response here"
}
```

For INCOMPLETE REQUESTS (missing origin, destination, or date), respond with:
```json
{
    "type": "conversation",
    "response": "Ask the user for the missing information"
}
```

RULES:
1. Extract the origin and destination cities/airports from the user's message
2. Extract the date - keep it EXACTLY as the user said it (e.g., "next friday", "this Saturday", "March 15", "tomorrow", "weekend")
3. Default adults to 1 unless specified
4. Default cabin_class to "ECONOMY" unless user mentions business/first class
5. Set return_date only for round trips
6. For greetings or non-search messages, use type "conversation"

IMPORTANT DATE EXTRACTION RULES:
- "next Friday" = the Friday of NEXT week (not this week)
- "this Friday" or "Friday" = the upcoming Friday (this week if not passed, otherwise next week)
- "weekend" = upcoming Saturday
- "next weekend" = Saturday of next week
- "tomorrow" = tomorrow's date
- Keep the EXACT wording the user used - don't change "next Friday" to "Friday"

HANDLING FOLLOW-UP QUESTIONS:
- If the user says "no, next Wednesday" or "change to Thursday", look at the PREVIOUS search to find origin and destination, then use the NEW date
- If the user says "what about to Singapore instead", keep the same origin and date but change the destination
- If the user provides a completely new search like "now check Beijing to Tokyo on March 5", treat it as a fresh search
- ALWAYS try to understand the user's intent from context
- When in doubt, ask for clarification rather than guessing

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

User: "find flights from Beijing to Singapore" (missing date)
```json
{
    "type": "conversation",
    "response": "I'd be happy to help you find flights from Beijing to Singapore! ✈️ When would you like to travel? For example, you could say 'tomorrow', 'next Friday', 'March 15', etc."
}
```

User: "find flights to Tokyo next Monday" (missing origin)
```json
{
    "type": "conversation",
    "response": "I can help you find flights to Tokyo next Monday! ✈️ Where will you be flying from?"
}
```

User: "find flights from New York next week" (missing destination)
```json
{
    "type": "conversation",
    "response": "Great! I can search for flights from New York next week. ✈️ Where would you like to fly to?"
}
```

User: "flights from Beijing to Singapore from March 1 to March 5" (date range - ambiguous)
```json
{
    "type": "date_range_clarification",
    "origin": "Beijing",
    "destination": "Singapore",
    "date_range_start": "March 1",
    "date_range_end": "March 5",
    "response": "I see you're looking at March 1 to March 5. Just to clarify:\n\n1️⃣ **Specific date**: Do you have a preferred departure date within this range?\n2️⃣ **Show all**: I can show you flights on any day between March 1-5\n\nWhich would you prefer? ✈️"
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

        # Delete stale results file BEFORE running the search
        # This prevents serving old data if the script crashes
        output_file = '/tmp/jetset_flights.json'
        if os.path.exists(output_file):
            os.remove(output_file)

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

        # Check if the script failed (non-zero exit code)
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            # Extract the last meaningful line of the traceback
            error_lines = [l for l in error_msg.split('\n') if l.strip() and not l.startswith('[')]
            short_error = error_lines[-1] if error_lines else error_msg[:200]
            logger.error(f"Flight search script failed (exit code {result.returncode}): {short_error}")
            return {"error": f"Flight search failed: {short_error}", "flights": [], "summary": {}}

        # Read results from file
        output_file = '/tmp/jetset_flights.json'
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                return json.load(f)

        return {"error": "No results file found - search may have failed", "flights": [], "summary": {}}

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

    # Show user's original date request vs parsed date for transparency
    user_date = params.get('date', '')
    date_display = f"{date}"
    if user_date.lower() != date.lower() and user_date.lower() not in date.lower():
        date_display = f"{date} (you said: '{user_date}')"

    response = f"""✈️ Found **{len(flights)} flights** from {origin} to {destination} on {date_display}!

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

        # Build enhanced system prompt with last search context
        enhanced_prompt = SYSTEM_PROMPT
        if conversation_id in last_search_params:
            last_params = last_search_params[conversation_id]

            # Check if we're awaiting date range clarification
            if last_params.get('awaiting_date_range_clarification'):
                enhanced_prompt += f"""

CONTEXT - AWAITING DATE RANGE CLARIFICATION:
The user previously mentioned dates from {last_params.get('date_range_start')} to {last_params.get('date_range_end')} for {last_params.get('origin')} to {last_params.get('destination')}.

If the user responds with:
- A specific date (e.g., "March 3", "the 10th", "1") → Set date to that specific date
- "show all" or "all" or "2" → Set date={last_params.get('date_range_start')} (use the start date to begin searching)
- Any other date preference → Use the date they mention

Extract the appropriate parameters for flight_search based on their response."""
            else:
                enhanced_prompt += f"""

CONTEXT - LAST SEARCH PARAMETERS:
- Origin: {last_params.get('origin', 'N/A')}
- Destination: {last_params.get('destination', 'N/A')}
- Date: {last_params.get('date', 'N/A')}
- Adults: {last_params.get('adults', 1)}
- Cabin Class: {last_params.get('cabin_class', 'ECONOMY')}

Use these as defaults if the user refers to them implicitly (e.g., "no, next Wednesday" means same origin/destination, different date)."""

        # Limit conversation history to last 10 messages for better context
        recent_history = conversations[conversation_id][:-1][-10:]

        result = call_claude_with_mcp(user_message, recent_history, system_prompt=enhanced_prompt)

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
            # Validate required parameters
            missing = []
            if not params.get('origin'):
                missing.append('origin')
            if not params.get('destination'):
                missing.append('destination')
            if not params.get('date'):
                missing.append('date')

            if missing:
                # Missing required parameters - ask for them
                logger.warning(f"Missing parameters: {missing}")
                missing_str = ', '.join(missing)
                assistant_message = f"I need a bit more information to search for flights. Could you please provide the {missing_str}? 😊"
            else:
                # Store these parameters as the last search
                last_search_params[conversation_id] = params.copy()

                # Run the fixed flight search script
                logger.info("Step 3: Running fixed flight search script...")
                flight_data = run_flight_search(params)

                # Generate friendly response from results
                logger.info("Step 4: Generating response...")
                assistant_message = generate_flight_response(flight_data, params)

        elif params.get('type') == 'date_range_clarification':
            # User provided a date range - need clarification
            # Store the date range context for next message
            last_search_params[conversation_id] = {
                'origin': params.get('origin'),
                'destination': params.get('destination'),
                'date_range_start': params.get('date_range_start'),
                'date_range_end': params.get('date_range_end'),
                'awaiting_date_range_clarification': True
            }
            assistant_message = params.get('response', "Please clarify your date preference.")

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
