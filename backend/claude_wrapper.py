import subprocess
import json
import logging
import requests
import os
import re

logger = logging.getLogger(__name__)

def call_claude_with_mcp(message, conversation_history=None):
    """
    Call Claude Code CLI with MCP tools enabled
    """
    try:
        # Build the prompt with conversation history
        if conversation_history and len(conversation_history) > 0:
            # Format conversation history
            context = "\n\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages for context
            ])
            full_prompt = f"{context}\n\nUser: {message}"
        else:
            full_prompt = message
        
        # Call Claude Code CLI using stdin for non-interactive execution
        result = subprocess.run(
            ['claude'],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=120,
            cwd='/workspace'
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'response': result.stdout.strip(),
                'error': None
            }
        else:
            logger.error(f"Claude CLI error: {result.stderr}")
            return {
                'success': False,
                'response': None,
                'error': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        logger.error("Claude CLI timeout")
        return {
            'success': False,
            'response': None,
            'error': 'Request timeout'
        }
    except Exception as e:
        logger.error(f"Claude CLI exception: {str(e)}")
        return {
            'success': False,
            'response': None,
            'error': str(e)
        }

def reformat_to_structured_json(raw_response, original_query):
    """
    Use Claude API to reformat the raw response into structured JSON
    """
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        base_url = os.getenv('ANTHROPIC_BASE_URL', 'http://44.251.199.189:4000/')
        model = os.getenv('ANTHROPIC_MODEL', 'claude-opus-4-5-20251101')
        
        # Check if response contains flight data (tables, prices, etc.)
        has_flight_data = bool(re.search(r'\$\d+|£\d+|€\d+|\d+h\s*\d+m|flight|airline', raw_response, re.IGNORECASE))
        
        if not has_flight_data:
            logger.info("No flight data detected in response, skipping JSON formatting")
            return None
        
        system_prompt = """You are a data extraction assistant. Your job is to extract flight information from text and convert it into structured JSON format.

Given flight information in any format (tables, lists, paragraphs), extract and return ONLY a valid JSON object with this exact structure:

{
  "flights": [
    {
      "id": "1",
      "airline": "Airline Name",
      "flightNumber": "XX123",
      "price": 123,
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
      "stops": 0,
      "layovers": [],
      "class": "Economy",
      "tags": []
    }
  ],
  "summary": {
    "totalResults": 5,
    "cheapestPrice": 123,
    "fastestDuration": "22h 50m",
    "averagePrice": 200
  }
}

Rules:
- Return ONLY the JSON object, no other text
- Use the currency symbol from the original text (USD, GBP, EUR)
- Convert prices to numbers (remove currency symbols)
- Add "cheapest" tag to the lowest priced flight
- Add "fastest" tag to the shortest duration flight
- If date is not specified, use tomorrow's date
- If flight number is not available, omit the field
- Extract all flights mentioned in the text"""

        user_prompt = f"""Extract flight data from this response and return as JSON:

{raw_response}

Original query: {original_query}

Return ONLY the JSON object, nothing else."""

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        payload = {
            'model': model,
            'max_tokens': 4096,
            'system': system_prompt,
            'messages': [
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ]
        }
        
        logger.info("Calling Claude API to reformat response into JSON...")
        
        response = requests.post(
            f'{base_url}v1/messages',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        
        # Extract text from response
        json_text = ""
        for block in result.get('content', []):
            if block.get('type') == 'text':
                json_text += block.get('text', '')
        
        # Try to extract JSON from the response
        # Look for JSON object
        json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
        if json_match:
            flight_data = json.loads(json_match.group(0))
            logger.info(f"Successfully extracted {len(flight_data.get('flights', []))} flights")
            return flight_data
        else:
            logger.warning("Could not find JSON in reformatted response")
            return None
            
    except Exception as e:
        logger.error(f"Error reformatting to JSON: {str(e)}")
        return None