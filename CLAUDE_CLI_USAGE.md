# Claude Code CLI Usage in JetSet AI

## The Difference Between Direct CLI and Backend Usage

### When You Run Directly in Terminal:
```bash
claude -p "Find flights from NYC to London next Friday"
```

**What happens:**
- Uses default Claude Code behavior
- No specific system prompt about using MCP tools
- May or may not use the booking.com MCP automatically
- Response depends on Claude's interpretation without guidance

### When Backend Calls Claude Code:
```bash
claude -p --system-prompt "You are JetSet, a travel agent..." "Find flights from NYC to London next Friday"
```

**What happens:**
- Uses custom system prompt that instructs Claude to use booking.com MCP
- Explicitly tells Claude to call MCP functions like `Search_Flight_Location` and `Search_Flights`
- Ensures Claude returns real flight data, not made-up information
- Provides consistent, structured responses

## The System Prompt

The backend includes this system prompt with every request:

```
You are JetSet, a friendly and professional AI travel agent assistant. 
You help users search for flights using natural language.

Your capabilities:
- You have access to the booking_com MCP tool to search for real flights
- You can understand natural language flight requests
- You extract: origin, destination, dates, number of passengers, class preferences, budget
- You provide flight recommendations with clear details

IMPORTANT: When a user asks about flights, you MUST:
1. Use the booking_com MCP tool to search for real flight data
2. Call the appropriate MCP functions like Search_Flight_Location and Search_Flights
3. Return actual flight results with prices, times, airlines, and durations
4. Format results in a clear, conversational way

Always use the MCP tools to get real data - never make up flight information!
```

## Why This Matters

### Without System Prompt (Direct CLI):
- Claude might just have a conversation about flights
- May not automatically use MCP tools
- Could provide generic advice instead of real data
- Inconsistent behavior

### With System Prompt (Backend):
- Claude knows it's a travel agent
- Explicitly instructed to use booking.com MCP
- Always searches for real flight data
- Consistent, reliable results

## How to Test the Same Way as Backend

If you want to test in terminal with the same behavior as the backend:

```bash
claude -p --system-prompt "You are JetSet, a travel agent with access to booking_com MCP. When users ask about flights, you MUST use the MCP tool to search for real flight data. Call Search_Flight_Location and Search_Flights functions." "Find flights from NYC to London next Friday"
```

## Backend Implementation

The backend code in `claude_wrapper.py`:

```python
def call_claude_with_mcp(message, conversation_history=None):
    system_prompt = """You are JetSet, a friendly and professional AI travel agent..."""
    
    result = subprocess.run(
        ['claude', '-p', '--system-prompt', system_prompt, full_prompt],
        capture_output=True,
        text=True,
        timeout=120,
        cwd='/workspace/jetset-ai'
    )
```

## Key Differences Summary

| Aspect | Direct CLI | Backend Usage |
|--------|-----------|---------------|
| System Prompt | None (default) | Custom travel agent prompt |
| MCP Usage | Optional/automatic | Explicitly required |
| Response Type | Conversational | Structured flight data |
| Consistency | Variable | Consistent |
| Real Data | Maybe | Always |

## Testing

### Test Direct CLI (No System Prompt):
```bash
cd /workspace/jetset-ai
claude -p "Find flights from NYC to London next Friday"
```

### Test With System Prompt (Like Backend):
```bash
cd /workspace/jetset-ai
claude -p --system-prompt "You are a travel agent. Use booking_com MCP to search for real flights." "Find flights from NYC to London next Friday"
```

### Test Via Backend API:
```bash
curl -X POST http://localhost:9002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find flights from NYC to London next Friday", "conversation_id": "test"}'
```

## Troubleshooting

### Issue: Direct CLI gives different results than backend
**Reason:** Direct CLI doesn't have the system prompt that instructs Claude to use MCP tools.

**Solution:** Either:
1. Use the backend API (recommended)
2. Add `--system-prompt` when testing directly
3. Create a project-specific configuration

### Issue: Claude doesn't use MCP tools
**Reason:** System prompt might not be explicit enough.

**Solution:** The backend now includes explicit instructions to use booking_com MCP functions.

### Issue: Timeout errors
**Reason:** MCP calls can take 30-60 seconds for flight searches.

**Solution:** Backend has 120-second timeout. Progress monitoring shows status during wait.

## Best Practices

1. **Always use the backend API** for consistent results
2. **Include system prompt** when testing CLI directly
3. **Monitor progress** using the `/api/progress` endpoint
4. **Check logs** in `~/.claude/projects/jetset-ai` for debugging
5. **Use Claude Monitor** dashboard to track token usage

## Example Workflow

1. User sends: "Find flights from NYC to London next Friday"
2. Backend receives request
3. Backend calls: `claude -p --system-prompt "..." "Find flights..."`
4. Claude Code:
   - Reads system prompt
   - Understands it needs to use booking_com MCP
   - Calls `Search_Flight_Location("NYC")` and `Search_Flight_Location("London")`
   - Calls `Search_Flights(origin, destination, date)`
   - Returns real flight data
5. Backend reformats response to structured JSON
6. Frontend displays flight cards

## Conclusion

The key difference is the **system prompt**. The backend includes a detailed system prompt that:
- Defines Claude's role as a travel agent
- Explicitly instructs it to use booking.com MCP
- Ensures real flight data is returned
- Provides consistent, structured responses

This is why direct CLI usage gives different results than going through the backend.