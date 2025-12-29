# Troubleshooting Guide - Common Issues & Solutions

Comprehensive guide for diagnosing and resolving common issues in the OpenAI Agents SDK project.

---

## Quick Diagnostic Commands

```bash
# Check Python version
python --version

# Verify virtual environment
which python  # macOS/Linux
where python  # Windows

# List installed packages
pip list | grep openai

# Test imports
python -c "from agents import Agent; from openai import OpenAI; print('OK')"

# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key:', os.getenv('OPENAI_API_KEY')[:10]+'...')"

# Run with verbose output
python -u agent.py
```

---

## Installation Issues

### Issue: `ModuleNotFoundError: No module named 'openai'`

**Symptoms**:
```
Traceback (most recent call last):
  File "agent.py", line 3, in <module>
    from openai import OpenAI
ModuleNotFoundError: No module named 'openai'
```

**Diagnosis**:
```bash
# Check if virtual environment is activated
echo $VIRTUAL_ENV  # Should show path to venv
```

**Solutions**:

1. **Activate virtual environment**:
   ```bash
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Reinstall dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Check pip is using correct Python**:
   ```bash
   which pip  # Should be venv/bin/pip
   pip --version
   ```

---

### Issue: `ImportError: cannot import name 'Agent' from 'agents'`

**Symptoms**:
```
ImportError: cannot import name 'Agent' from 'agents'
```

**Diagnosis**:
```bash
# Check openai-agents version
pip show openai-agents
```

**Solutions**:

1. **Upgrade openai-agents**:
   ```bash
   pip install --upgrade openai-agents
   ```

2. **Verify SDK version compatibility**:
   ```bash
   # Check installed version
   pip show openai-agents
   
   # Should be 0.1.0 or higher
   ```

3. **Reinstall from scratch**:
   ```bash
   pip uninstall openai-agents
   pip install openai-agents
   ```

---

### Issue: PowerShell execution policy error

**Symptoms**:
```
.\venv\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled on this system.
```

**Solution**:
```powershell
# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation
.\venv\Scripts\Activate.ps1
```

---

## API Key Issues

### Issue: `openai.AuthenticationError: Invalid API key`

**Symptoms**:
```
openai.AuthenticationError: Error code: 401 - {'error': {'message': 'Incorrect API key provided'}}
```

**Diagnosis**:
```bash
# Check .env file exists
ls -la .env  # macOS/Linux
dir .env     # Windows

# Check .env contents (first 10 chars only for security)
cat .env | head -c 50  # macOS/Linux
type .env             # Windows
```

**Solutions**:

1. **Verify API key format**:
   ```bash
   # OpenAI keys start with sk-proj- or sk-
   # Should be 51+ characters long
   ```

2. **Check .env loading**:
   ```python
   # Test script: test_env.py
   import os
   from dotenv import load_dotenv, find_dotenv
   
   print("Looking for .env file...")
   env_path = find_dotenv()
   print(f"Found: {env_path}")
   
   load_dotenv(env_path)
   
   api_key = os.getenv('OPENAI_API_KEY')
   if api_key:
       print(f"API key loaded: {api_key[:10]}...")
   else:
       print("ERROR: API key not found!")
   ```
   
   ```bash
   python test_env.py
   ```

3. **Regenerate API key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Delete old key
   - Create new key
   - Update `.env` file

4. **Check for whitespace**:
   ```bash
   # .env file should have NO spaces around =
   # ✅ Correct:
   OPENAI_API_KEY=sk-proj-xxxxx
   
   # ❌ Wrong:
   OPENAI_API_KEY = sk-proj-xxxxx
   ```

---

### Issue: API key has insufficient credits

**Symptoms**:
```
openai.RateLimitError: You exceeded your current quota, please check your plan and billing details.
```

**Solution**:
1. Check billing: [OpenAI Billing](https://platform.openai.com/account/billing)
2. Add payment method if needed
3. Check usage limits: [Usage Dashboard](https://platform.openai.com/usage)

---

## Runtime Errors

### Issue: `asyncio.run() cannot be called from running event loop`

**Symptoms**:
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

**Diagnosis**:
- Occurs in Jupyter notebooks or when already in async context

**Solutions**:

1. **Use await directly** (if already in async context):
   ```python
   # Instead of:
   asyncio.run(main())
   
   # Use:
   await main()
   ```

2. **Use nest_asyncio** (in Jupyter):
   ```python
   import nest_asyncio
   nest_asyncio.apply()
   
   asyncio.run(main())
   ```

---

### Issue: `pydantic.ValidationError: output validation failed`

**Symptoms**:
```
pydantic.ValidationError: 3 validation errors for TravelOutput
destination
  field required (type=value_error.missing)
```

**Diagnosis**:
- LLM returned invalid JSON structure
- Output doesn't match Pydantic model

**Solutions**:

1. **Check raw output**:
   ```python
   result_content = response.choices[0].message.content
   print("Raw output:", result_content)
   ```

2. **Improve instructions**:
   ```python
   instructions = (
       "You MUST return ONLY valid JSON matching this EXACT structure: "
       '{"destination": "string", "duration": "string", "summary": "string"}'
       "Do NOT include any text before or after the JSON."
   )
   ```

3. **Add output parsing fallback**:
   ```python
   def print_fields(data):
       if isinstance(data, str):
           try:
               # Try to parse JSON
               parsed = json.loads(data)
               data = TravelOutput(**parsed)
           except (json.JSONDecodeError, ValidationError) as e:
               print("Parsing failed:", e)
               print("Raw output:", data)
               return
       
       # Display fields
       print(f"Destination: {data.destination}")
       print(f"Duration: {data.duration}")
       print(f"Summary: {data.summary}")
   ```

4. **Lower temperature** (more deterministic):
   ```python
   response = client.chat.completions.create(
       model="gpt-4",
       temperature=0.2,  # Lower = more consistent
       ...
   )
   ```

---

### Issue: `InputGuardrailTripwireTriggered` exception

**Symptoms**:
```
agents.guardrails.InputGuardrailTripwireTriggered: Guardrail triggered
```

**Diagnosis**:
- Guardrail validation failed
- Input blocked before processing

**Solutions**:

1. **Check guardrail reasoning**:
   ```python
   async def budget_guardrail(ctx, agent, input_data):
       result = await Runner.run(budget_guardrail_agent, input_data)
       final_output = result.final_output_as(BudgetCheckOutput)
       
       print("Guardrail reasoning:", final_output.reasoning)  # ⭐ Debug output
       
       return GuardrailFunctionOutput(
           output_info=final_output,
           tripwire_triggered=not final_output.is_valid
       )
   ```

2. **Handle gracefully**:
   ```python
   try:
       result = await Runner.run(travel_agent, prompt)
   except InputGuardrailTripwireTriggered as e:
       print("Request blocked:", e)
       # Provide user feedback
       print("Please adjust your budget and try again")
   ```

3. **Adjust guardrail logic**:
   ```python
   # If guardrail is too strict, modify instructions
   budget_guardrail_agent = Agent(
       instructions=(
           "Only flag budgets that are EXTREMELY unrealistic. "
           "Small budgets are OK if plausible for destination."
       ),
       ...
   )
   ```

---

## Tool Execution Issues

### Issue: Tool not being called by agent

**Symptoms**:
- Agent doesn't use web_search even though it's available
- No tool_calls in response

**Diagnosis**:
```python
response = client.chat.completions.create(
    model="llama3.2",
    messages=messages,
    tools=tools
)

message = response.choices[0].message
print("Tool calls:", message.tool_calls)  # None or empty
```

**Solutions**:

1. **Improve tool description**:
   ```python
   tools = [
       {
           "type": "function",
           "function": {
               "name": "web_search",
               "description": (
                   "Search the web for current information about travel destinations, "
                   "hotels, restaurants, attractions, and prices. "
                   "Use this when you need up-to-date information not in your training data."
               ),
               ...
           }
       }
   ]
   ```

2. **Explicitly instruct agent to use tools**:
   ```python
   instructions = (
       "You are a travel planner. "
       "You MUST use the web_search tool to find current information. "
       "Always search for: destination details, hotel prices, and local attractions."
   )
   ```

3. **Force tool use** (if appropriate):
   ```python
   response = client.chat.completions.create(
       model="llama3.2",
       messages=messages,
       tools=tools,
       tool_choice="required"  # ⭐ Force at least one tool call
   )
   ```

---

### Issue: Tool execution fails

**Symptoms**:
```
Error: HTTPError: 403 Client Error: Forbidden for url
```

**Diagnosis**:
- External API (DuckDuckGo) returning error
- Network connectivity issues

**Solutions**:

1. **Add error handling to tool**:
   ```python
   def web_search(query):
       try:
           url = f"https://api.duckduckgo.com/?q={query}&format=json"
           response = requests.get(url, timeout=10)
           response.raise_for_status()
           data = response.json()
           return data.get('AbstractText', 'No results found')
       except requests.exceptions.Timeout:
           return "Search timed out. Please try again."
       except requests.exceptions.HTTPError as e:
           return f"Search failed: {e.response.status_code}"
       except Exception as e:
           return f"Search error: {str(e)}"
   ```

2. **Test tool independently**:
   ```python
   # Test script: test_tool.py
   import requests
   
   query = "Paris travel"
   url = f"https://api.duckduckgo.com/?q={query}&format=json"
   response = requests.get(url)
   print(f"Status: {response.status_code}")
   print(f"Result: {response.json()}")
   ```

3. **Use alternative search API**:
   ```python
   # Google Custom Search, Bing API, etc.
   ```

---

## Ollama Issues (Lessons 1-3)

### Issue: `Connection refused` when using Ollama

**Symptoms**:
```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded
```

**Diagnosis**:
```bash
# Check if Ollama server is running
curl http://localhost:11434/api/tags
```

**Solutions**:

1. **Start Ollama server**:
   ```bash
   ollama serve
   ```

2. **Pull model**:
   ```bash
   ollama pull llama3.2
   ```

3. **Verify model exists**:
   ```bash
   ollama list
   # Should show llama3.2
   ```

4. **Check port**:
   ```bash
   # Default port is 11434
   # If changed, update base_url in code
   ```

---

### Issue: Ollama model not found

**Symptoms**:
```
Error: model 'llama3.2' not found
```

**Solution**:
```bash
# Pull model
ollama pull llama3.2

# Verify
ollama list
```

---

## Session Issues (Lesson 5)

### Issue: Session not persisting

**Symptoms**:
- Agent doesn't remember previous conversation
- Each run starts fresh

**Diagnosis**:
```python
session = SQLiteSession("user_123")
print("Session ID:", session.session_id)

# Check if session has messages
# (implementation-specific)
```

**Solutions**:

1. **Verify session is passed to Runner**:
   ```python
   # ✅ Correct:
   result = await Runner.run(agent, prompt, session=session)
   
   # ❌ Wrong:
   result = await Runner.run(agent, prompt)  # No session!
   ```

2. **Use same session instance**:
   ```python
   # ✅ Correct:
   session = SQLiteSession("user_123")
   result1 = await Runner.run(agent, "Request 1", session=session)
   result2 = await Runner.run(agent, "Request 2", session=session)
   
   # ❌ Wrong:
   session1 = SQLiteSession("user_123")
   result1 = await Runner.run(agent, "Request 1", session=session1)
   
   session2 = SQLiteSession("user_123")  # Different instance!
   result2 = await Runner.run(agent, "Request 2", session=session2)
   ```

3. **Check session storage**:
   ```python
   # For file-based SQLite:
   # Check if database file exists
   import os
   print("Session DB exists:", os.path.exists("sessions.db"))
   ```

---

## Performance Issues

### Issue: Slow response times

**Symptoms**:
- Agent takes 30+ seconds to respond
- Timeouts

**Solutions**:

1. **Reduce reasoning effort**:
   ```python
   model_settings = ModelSettings(
       reasoning={"effort": "low"}  # Instead of "medium" or "high"
   )
   ```

2. **Lower verbosity**:
   ```python
   model_settings = ModelSettings(
       extra_body={"text": {"verbosity": "low"}}
   )
   ```

3. **Simplify instructions**:
   ```python
   # Keep instructions concise
   # Avoid overly complex requirements
   ```

4. **Use faster model**:
   ```python
   agent = Agent(
       model="gpt-4",  # Faster than gpt-5 for simple tasks
       ...
   )
   ```

5. **Add timeout**:
   ```python
   import asyncio
   
   try:
       result = await asyncio.wait_for(
           Runner.run(agent, prompt),
           timeout=30.0  # 30 seconds
       )
   except asyncio.TimeoutError:
       print("Agent execution timed out")
   ```

---

## Debugging Techniques

### Enable Debug Logging

```python
import logging

# Enable debug logging for all modules
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or specific modules
logging.getLogger('openai').setLevel(logging.DEBUG)
logging.getLogger('agents').setLevel(logging.DEBUG)
```

### Inspect API Requests/Responses

```python
from openai import OpenAI
import logging

# Enable HTTP request logging
logging.getLogger("httpx").setLevel(logging.DEBUG)

client = OpenAI(api_key=...)
response = client.chat.completions.create(...)

# This will print full HTTP request/response
```

### Trace Agent Execution

```python
async def main():
    result = await Runner.run(agent, prompt)
    
    # Inspect result
    print("Messages:", result.messages)
    print("Tool calls:", result.tool_calls)
    print("Final output:", result.final_output)
```

### Use Python Debugger

```python
import pdb

def main():
    # Set breakpoint
    pdb.set_trace()
    
    response = client.chat.completions.create(...)
```

```bash
# Run with debugger
python -m pdb agent.py
```

---

## Common Error Messages Reference

| Error | Meaning | Solution |
|-------|---------|----------|
| `ModuleNotFoundError` | Package not installed | `pip install <package>` |
| `AuthenticationError` | Invalid API key | Check `.env` file |
| `RateLimitError` | Too many requests / no credits | Wait or add credits |
| `ValidationError` | Invalid output structure | Improve instructions |
| `ConnectionError` | Can't reach API | Check network/firewall |
| `TimeoutError` | Request took too long | Increase timeout |
| `InputGuardrailTripwireTriggered` | Guardrail blocked request | Check guardrail logic |

---

## When to Ask for Help

If you've tried the above solutions and still have issues:

1. **Gather diagnostic info**:
   ```bash
   # System info
   python --version
   pip list
   
   # Error trace
   python agent.py 2>&1 | tee error.log
   ```

2. **Minimal reproducible example**:
   ```python
   # Create simplest possible code that reproduces issue
   from openai import OpenAI
   
   client = OpenAI(api_key="...")
   response = client.chat.completions.create(
       model="gpt-4",
       messages=[{"role": "user", "content": "Hi"}]
   )
   print(response.choices[0].message.content)
   ```

3. **Document what you tried**:
   - List all solutions attempted
   - Include error messages
   - Note any changes in behavior

---

## Additional Resources

- **OpenAI API Status**: [status.openai.com](https://status.openai.com)
- **OpenAI Community**: [community.openai.com](https://community.openai.com)
- **Agents SDK Issues**: [GitHub Issues](https://github.com/openai/openai-python)

---

**Document Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**Target Audience**: All Developers
