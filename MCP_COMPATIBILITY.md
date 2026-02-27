# MCP Server Compatibility

## Problem Solved

The app needs to work in **multiple environments** with different MCP server configurations:

| Environment | MCP Server | Tool Prefix | Example Tool Name |
|-------------|-----------|-------------|-------------------|
| **Local LiteLLM** | `booking_com_mcp` (alias: `flights`) | `flights-` | `flights-Search_Flight_Location` |
| **Sandbox** | Multiple servers with `flights` alias | `flights-` | `flights-Search_Flight_Location` |
| **Alternative** | Various naming patterns | Varies | Could be any pattern |

Previously, hardcoding configurations caused failures when moving between environments.

## Solution

### 1. **Smart Auto-Discovery**

The client now tries **multiple discovery patterns** in priority order:

```python
# Priority 1: Server with alias "flights" (most common)
# Priority 2: Server with "booking" in name
# Priority 3: Server with "flight" or "travel" in name
```

### 2. **Automatic Retry with Multiple Tool Prefixes**

When a tool call fails with 404 (not found), it automatically retries with different prefixes:

```python
tool_patterns = [
    "flights-Search_Flight_Location",    # Primary
    "Search_Flight_Location",             # Fallback 1: No prefix
    "booking_com-Search_Flight_Location", # Fallback 2: Alternative prefix
]
```

The **first successful pattern is cached** for future calls, making subsequent requests fast.

### 3. **Always Run Discovery**

Even if `BOOKING_MCP_SERVER_ID` is set in `.env`, the system runs discovery to ensure `tool_prefix` is correct.

## Configuration Options

### Option 1: Full Auto (Recommended)

Don't set anything - let discovery handle it:

```bash
# In backend/.env
ANTHROPIC_API_KEY=your-key
ANTHROPIC_BASE_URL=http://0.0.0.0:4000

# BOOKING_MCP_SERVER_ID not set - auto-discovery runs
```

### Option 2: Partial Config (Advanced)

Set server_id but let discovery set tool_prefix:

```bash
BOOKING_MCP_SERVER_ID=55bb332b-cdff-4f8a-8a09-4de3b5d3e913
# Tool prefix will be discovered automatically
```

### Option 3: Full Manual (Not Recommended)

```python
from booking_com_client import BookingCom, BookingConfig

config = BookingConfig(
    base_url="http://0.0.0.0:4000",
    api_key="your-key",
    server_id="55bb332b-cdff-4f8a-8a09-4de3b5d3e913",
    tool_prefix="flights-"
)
booking = BookingCom(config)
```

## How It Works

### Discovery Process

```
1. Check if server has alias "flights"
   ✓ Most reliable - specifically for flight bookings
   └─> Set prefix to "flights-"

2. Check if server_name contains "booking"
   ✓ Broader match for booking.com servers
   └─> Set prefix to "{alias}-" or ""

3. Check if server_name contains "flight" or "travel"
   ✓ Fallback for other naming conventions
   └─> Set prefix to "{alias}-" or ""
```

### Tool Call Process

```
1. Try: {prefix}Tool_Name (e.g., "flights-Search_Flight_Location")
   └─> 404? Try next pattern

2. Try: Tool_Name (no prefix)
   └─> 404? Try next pattern

3. Try: booking_com-Tool_Name
   └─> 404? Fail with error

✓ Success? Cache the working prefix for future calls
```

## Testing

### Run Compatibility Test

```bash
cd /Users/yu.yan/code/agent-jetset-ai
python3 test_mcp_compatibility.py
```

**Expected Output:**
```
✓ Server ID: 55bb332b-cdff-4f8a-8a09-4de3b5d3e913
✓ Tool Prefix: 'flights-'
✓ Base URL: http://0.0.0.0:4000
✓ Success! Found 11 airports/cities
```

### Test in Different Environments

**Local:**
```bash
# Uses LiteLLM on port 4000
cd backend
source .venv/bin/activate
python app.py
```

**Sandbox:**
```bash
# Uses sandbox MCP gateway
cd /workspace/backend
source .venv/bin/activate
python app.py
```

Both should work **without any code changes**.

## Debugging

### Check Discovery Output

The client prints debug info during discovery:
```
[MCP] Using server 'booking_com_mcp' with alias 'flights'
```

### Verify Tool Prefix

```python
from booking_com_client import BookingCom

booking = BookingCom()
print(f"Server ID: {booking.config.server_id}")
print(f"Tool Prefix: '{booking.config.tool_prefix}'")
```

### Check Available Servers

```bash
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  "$ANTHROPIC_BASE_URL/v1/mcp/server" | jq '.[] | {server_name, alias}'
```

## Improvements Made

| Issue | Before | After |
|-------|--------|-------|
| **Server discovery** | Only looked for "booking" in name | Multi-pattern: "flights" alias → "booking" name → "flight"/"travel" name |
| **Tool prefix** | Not set when server_id in env | Always discovered, even with env var |
| **Tool call failures** | Immediate failure | Auto-retry with 3 different prefix patterns |
| **Caching** | No optimization | Successful pattern cached for speed |
| **Environment portability** | Manual config changes needed | Works everywhere automatically |

## Files Changed

| File | Changes |
|------|---------|
| `backend/booking_com_client.py` | - Enhanced discovery with 3 priority levels<br>- Added auto-retry with multiple tool prefixes<br>- Always run discovery for tool_prefix<br>- Added debug logging |
| `backend/.env` | - Commented out hardcoded BOOKING_MCP_SERVER_ID |
| `test_mcp_compatibility.py` | - New comprehensive compatibility test |
| `MCP_COMPATIBILITY.md` | - This documentation |

## For Jira

**Feature #29: Cross-Environment MCP Compatibility**
- **Type**: Feature + Bug Fix
- **Description**: Automatic discovery and retry logic ensures app works with different MCP server configurations (local LiteLLM, sandbox, alternative naming). No manual config changes needed when deploying.
- **Impact**: Deploy once, runs everywhere - eliminates environment-specific bugs
- **Files**: `booking_com_client.py`, `.env`, `test_mcp_compatibility.py`, `MCP_COMPATIBILITY.md`

## Total Improvements: 29 🚀
