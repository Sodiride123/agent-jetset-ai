# Bug Fix: Claude CLI Integration Issue

## Problem
When users queried the JetSet AI application through the web interface, they received the error:
```
I apologize, but I'm having trouble connecting right now. Please try again in a moment! 😊
```

However, when running `claude -p "query"` directly from the terminal, it worked correctly and returned real flight data via MCP tools.

## Root Cause
The issue was in how the backend Python subprocess was calling Claude CLI:

### Original Code (Not Working):
```python
result = subprocess.run(
    ['claude', '-p', full_prompt],
    capture_output=True,
    text=True,
    timeout=120,
    cwd='/workspace/jetset-ai'
)
```

**Problem**: The `-p` (print mode) flag was causing Claude CLI to hang indefinitely when called from a Python subprocess, even though it worked fine from the terminal.

### Attempted Solutions That Failed:
1. **Adding `--dangerously-skip-permissions`**: This flag cannot be used with root privileges
2. **Checking conversation history**: Fixed a minor bug but didn't resolve the main issue
3. **Verifying working directory**: The `cwd` parameter was correctly set

## Solution
Changed the subprocess call to use **stdin** instead of the `-p` flag:

### Fixed Code (Working):
```python
result = subprocess.run(
    ['claude'],
    input=full_prompt,  # Pass prompt via stdin instead of -p flag
    capture_output=True,
    text=True,
    timeout=120,
    cwd='/workspace/jetset-ai'
)
```

## Why This Works
- The `-p` flag is designed for interactive terminal use and may wait for user input or permissions
- Using stdin (`input=full_prompt`) provides a non-interactive way to pass the prompt
- Claude CLI still has access to MCP tools and project configuration when run from the correct directory
- The subprocess completes successfully and returns real flight data

## Test Results
**Query**: "Find flights from London to Tokyo in March"

**Response Time**: ~63 seconds

**Result**: Successfully returned 6 real flights with complete details:
- Cheapest: £328 (China Southern via Beijing)
- Fastest: 17h 30m (China Eastern + Spring Airlines via Shanghai)
- All flights include: airline, departure/arrival times, airports, duration, stops, layovers, prices

## Files Modified
1. `backend/claude_wrapper.py` - Changed subprocess call method

## Additional Fixes
1. Fixed conversation history handling to check for empty lists
2. Ensured proper working directory context for Claude CLI

## Verification
✅ Backend API responds correctly  
✅ MCP tools are accessed successfully  
✅ Real flight data is retrieved from booking.com  
✅ Structured JSON is properly formatted  
✅ Frontend displays flight cards correctly  

**Status**: Bug fixed and verified working in production.