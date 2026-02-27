import subprocess
import json
import logging
import requests
import os
import re
import sys

logger = logging.getLogger(__name__)

def call_claude_with_mcp(message, conversation_history=None, system_prompt=None):
    """
    Call Claude Code CLI with MCP tools enabled and system prompt for booking_com_client usage
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
        
        # Build Claude CLI command with system prompt and custom settings
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'settings.json')
        cmd = ['claude', '--print', '--settings', settings_path]
        if system_prompt:
            cmd.extend(['--system-prompt', system_prompt])
        
        logger.info(f"Running Claude CLI: {' '.join(cmd[:5])}...")
        
        # Call Claude Code CLI using stdin for non-interactive execution
        # Auto-detect environment: /workspace (sandbox) or local project root
        project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        working_dir = '/workspace' if os.path.exists('/workspace') else project_root

        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout for flight searches
            cwd=working_dir
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
    Extract structured JSON from the response. First checks for file-based output,
    then tries direct extraction from code blocks, then falls back to API call if needed.
    """
    try:
        # PRIORITY 1: Check for file-based JSON (new fast approach)
        file_match = re.search(r'FLIGHT_FILE_SAVED:(/[^\s\n]+\.json)', raw_response)
        if file_match:
            file_path = file_match.group(1)
            logger.info(f"Found flight file marker, reading from: {file_path}")
            try:
                with open(file_path, 'r') as f:
                    flight_data = json.load(f)
                if 'flights' in flight_data and isinstance(flight_data['flights'], list):
                    logger.info(f"Successfully loaded {len(flight_data.get('flights', []))} flights from file")
                    return flight_data
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to read flight file {file_path}: {e}")

        # Also check the default file location even without marker
        default_file = '/tmp/jetset_flights.json'
        if os.path.exists(default_file):
            try:
                # Check if file was modified recently (within last 5 minutes)
                import time
                file_mtime = os.path.getmtime(default_file)
                if time.time() - file_mtime < 300:  # 5 minutes
                    with open(default_file, 'r') as f:
                        flight_data = json.load(f)
                    if 'flights' in flight_data and isinstance(flight_data['flights'], list):
                        logger.info(f"Loaded {len(flight_data.get('flights', []))} flights from default file")
                        return flight_data
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to read default flight file: {e}")

        # PRIORITY 2: Try multiple extraction patterns in order of preference
        extraction_patterns = [
            (r'FLIGHT_JSON_START\s*(\{.*\})\s*FLIGHT_JSON_END', "FLIGHT_JSON markers"),
            (r'```json\s*(\{.*\})\s*```', "```json blocks"),
            (r'JSON OUTPUT:\s*(\{.*\})', "JSON OUTPUT prefix"),
            (r'FLIGHT SEARCH RESULTS JSON[:\s=]*(\{.*\})', "FLIGHT SEARCH RESULTS"),
            (r'"flights"\s*:\s*\[.*?\]\s*,\s*"summary"', "flights+summary structure"),
        ]

        for pattern, pattern_name in extraction_patterns[:-1]:  # Skip last pattern (it's a detection pattern)
            match = re.search(pattern, raw_response, re.DOTALL)
            if match:
                try:
                    json_text = match.group(1)
                    flight_data = json.loads(json_text)
                    if 'flights' in flight_data and isinstance(flight_data['flights'], list):
                        logger.info(f"Extracted {len(flight_data.get('flights', []))} flights using {pattern_name}")
                        return flight_data
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from {pattern_name}: {e}")
                    continue

        # Last resort: find any JSON object with "flights" key
        json_block_match = re.search(r'(\{"flights"\s*:\s*\[.*\]\s*,\s*"summary"\s*:\s*\{[^}]+\}\s*\})', raw_response, re.DOTALL)
        if json_block_match:
            try:
                json_text = json_block_match.group(1)
                flight_data = json.loads(json_text)
                # Validate it has the expected structure
                if 'flights' in flight_data and isinstance(flight_data['flights'], list):
                    logger.info(f"Directly extracted {len(flight_data.get('flights', []))} flights from response")
                    return flight_data
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON block directly: {e}")

        # Check if response contains flight data (tables, prices, etc.)
        has_flight_data = bool(re.search(r'\$\d+|£\d+|€\d+|\d+h\s*\d+m|flight|airline', raw_response, re.IGNORECASE))

        if not has_flight_data:
            logger.info("No flight data detected in response, skipping JSON formatting")
            return None

        # Fall back to API call only if direct extraction failed
        logger.info("Direct JSON extraction failed, falling back to API call...")
        api_key = os.getenv('ANTHROPIC_API_KEY')
        base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')
        model = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
        
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
      "tags": [],
      "token": "d6a1f_H4sIAAAAAAAA_..."
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
- Extract all flights mentioned in the text
- CRITICAL: EVERY flight in the response has a unique "token" field. You MUST extract and include the token for EACH flight, not just the first one. The token is a long string (often starting with characters like "d6a1f_" or similar). Extract ALL tokens from ALL flights."""

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
            f'{base_url.rstrip("/")}/v1/messages',
            headers=headers,
            json=payload,
            timeout=120
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
