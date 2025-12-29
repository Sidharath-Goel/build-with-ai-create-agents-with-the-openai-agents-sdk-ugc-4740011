# Lesson-by-Lesson Guide - Code Walkthrough

Comprehensive code walkthrough for each lesson with line-by-line explanations, learning objectives, and key takeaways.

---

## How to Use This Guide

1. **Read lesson overview** - Understand learning objectives
2. **Study code blocks** - Follow annotated code samples
3. **Run the code** - Execute `agent.py` in each folder
4. **Experiment** - Modify parameters and observe changes
5. **Move to next lesson** - Build on previous knowledge

---

## Lesson 1: Create the Core Travel Agent

### Learning Objectives
- ✅ Understand basic agent creation
- ✅ Define structured outputs with Pydantic
- ✅ Make OpenAI API calls
- ✅ Parse and validate JSON responses

### File Location
[1 Create the Core Travel Agent/agent.py](../1%20Create%20the%20Core%20Travel%20Agent/agent.py)

### Complete Code Walkthrough

#### Step 1: Imports and Setup
```python
import asyncio  # For async operations (not used in L1, but pattern for L4+)
import json     # JSON parsing

from openai import OpenAI                    # OpenAI Python client
from pydantic import BaseModel, ValidationError  # Data validation
```

**Purpose**: Load required libraries for API calls and validation.

#### Step 2: Client Configuration
```python
# Ollama client (local LLM for development)
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama server endpoint
    api_key="ollama"                       # Dummy key for local
)
```

**Key Insight**: This uses Ollama (local LLM) instead of OpenAI API. For production, use:
```python
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
```

#### Step 3: Define Output Schema
```python
class TravelOutput(BaseModel):
    """
    Structured output format using Pydantic.
    Ensures LLM returns consistent, parseable data.
    """
    destination: str  # Where to travel
    duration: str     # Trip length (e.g., "3 days")
    summary: str      # Brief trip description
```

**Why Pydantic?**
- ✅ Automatic validation
- ✅ Type safety
- ✅ Easy JSON serialization
- ✅ IDE autocomplete support

#### Step 4: Agent Instructions
```python
instructions = (
    "You are a friendly and knowledgeable travel planner that helps users plan trips, "
    "suggest destinations, and create brief summaries of their journeys. "
    "Always return your response as valid JSON matching this structure: "
    '{"destination": "string", "duration": "string", "summary": "string"}'
)
```

**Instruction Engineering Tips**:
1. **Define role**: "You are a friendly travel planner"
2. **Specify output format**: "Return as valid JSON"
3. **Provide schema**: Show exact structure expected
4. **Be explicit**: Clear instructions = better results

#### Step 5: Output Display Helper
```python
def print_fields(data):
    """
    Parse and display agent output.
    Handles both raw JSON strings and Pydantic objects.
    """
    if isinstance(data, str):
        try:
            # Try to parse string as TravelOutput
            data = TravelOutput(**json.loads(data))
        except (json.JSONDecodeError, ValidationError) as e:
            # If parsing fails, show raw output
            print("Raw output:", data)
            return
    
    # Display structured fields
    print(f"Destination: {data.destination}")
    print(f"Duration: {data.duration}")
    print(f"Summary: {data.summary}")
```

**Error Handling**: Gracefully handles malformed JSON or validation errors.

#### Step 6: Main Execution Logic
```python
def main():
    print("Starting agent...")
    try:
        print("Calling Ollama API...")
        response = client.chat.completions.create(
            model="llama3.2",          # Local Llama model
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": "Plan a 3-day trip to Mussoorie under INR 5000..."}
            ],
            temperature=0.7            # Creativity level (0-2, higher = more creative)
        )
        print("API call successful.")
        
        # Extract response text
        result_content = response.choices[0].message.content
        print(f"Raw response: {result_content}")
        
        # Display formatted output
        print_fields(result_content)
    except Exception as e:
        print("Error", e)
```

**API Call Breakdown**:
- `model`: LLM to use (llama3.2 for local, gpt-4 for OpenAI)
- `messages`: Conversation history (system + user)
- `temperature`: Randomness (0.7 = balanced)

#### Step 7: Entry Point
```python
if __name__ == "__main__":
    main()
```

**Purpose**: Runs `main()` only when script is executed directly (not imported).

### Expected Output
```
Starting agent...
Calling Ollama API...
API call successful.
Raw response: {"destination":"Mussoorie","duration":"3 days","summary":"..."}
Destination: Mussoorie
Duration: 3 days
Summary: A 3-day budget trip exploring hidden gems in Mussoorie...
```

### Key Takeaways
✅ **Agent = Instructions + Model + Output Schema**  
✅ **Pydantic enforces structure** on LLM outputs  
✅ **System messages** define agent behavior  
✅ **User messages** provide input  

### Experiment Ideas
1. Change destination in user prompt
2. Modify `temperature` (0.1 for deterministic, 1.5 for creative)
3. Add fields to `TravelOutput` (e.g., `budget: str`)
4. Adjust instructions to change agent personality

---

## Lesson 2: Extend the Agent with Tools

### Learning Objectives
- ✅ Integrate external functions as tools
- ✅ Enable agent to call tools autonomously
- ✅ Handle multi-turn tool execution
- ✅ Process tool results and continue reasoning

### New Concepts
- **Tool Calling**: LLM decides when to call functions
- **Function Schemas**: JSON schema describing tools
- **Tool Execution Loop**: LLM → Tool → LLM → Output

### Code Additions

#### Tool Implementation
```python
def web_search(query):
    """
    Search DuckDuckGo for information.
    
    Args:
        query: Search query string
    
    Returns:
        str: Search results or error message
    """
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url)
        data = response.json()
        return data.get('AbstractText', data.get('Answer', 'No information found'))
    except Exception as e:
        return f"Error searching: {e}"
```

**Tool Pattern**: Simple function that returns string result.

#### Tool Schema Definition
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",           # Function name (must match Python function)
            "description": "Search the web for information about a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]       # Mandatory parameters
            }
        }
    }
]
```

**Schema Purpose**: LLM uses this to understand:
- When to call the tool
- What parameters to pass
- What data type to expect

#### Tool Execution Logic
```python
response = client.chat.completions.create(
    model="llama3.2",
    messages=messages,
    temperature=0.7,
    tools=tools  # ⭐ NEW: Provide available tools
)

message = response.choices[0].message

# Check if LLM wants to call a tool
if message.tool_calls:
    for tool_call in message.tool_calls:
        if tool_call.function.name == "web_search":
            # Extract arguments
            args = json.loads(tool_call.function.arguments)
            
            # Execute tool
            result = web_search(args['query'])
            
            # Send result back to LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
    
    # Call LLM again with tool results
    response = client.chat.completions.create(
        model="llama3.2",
        messages=messages,
        temperature=0.7,
        tools=tools
    )
```

**Execution Flow**:
1. LLM receives user request
2. LLM decides to call `web_search("Mussoorie travel tips")`
3. Your code executes `web_search()` function
4. Result appended to message history
5. LLM continues reasoning with tool data
6. LLM returns final answer

### Tool Call Example

**User**: "Plan a 3-day trip to Mussoorie"

**LLM Thinks**: "I need current information about Mussoorie"

**LLM Calls**: `web_search(query="Mussoorie attractions 2025")`

**Tool Returns**: "Mussoorie is a hill station known for..."

**LLM Synthesizes**: Uses tool data to create trip plan

**Final Output**: JSON with destination, duration, summary (enriched with web data)

### Key Takeaways
✅ **Tools extend agent capabilities** beyond training data  
✅ **LLM autonomously decides** when to use tools  
✅ **Multi-turn execution** allows complex reasoning  
✅ **Tool schemas are critical** for proper LLM understanding  

---

## Lesson 3: Orchestrate Multiple Agents

### Learning Objectives
- ✅ Implement multi-agent architecture
- ✅ Delegate tasks to specialized agents
- ✅ Coordinate agent outputs
- ✅ Handle complex orchestration logic

### Architecture Pattern

```
              User Request
                    ↓
            ┌───────────────┐
            │ Orchestrator  │  (Decides which agents to call)
            └───────┬───────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   ┌────────┐  ┌────────┐  ┌────────┐
   │Planner │  │ Budget │  │ Guide  │
   └────────┘  └────────┘  └────────┘
        │           │           │
        └───────────┴───────────┘
                    ↓
            Aggregated Output
```

### Specialized Agent Implementations

#### Planner Agent
```python
def planner_agent(user_prompt):
    """
    Specialist: Day-by-day itinerary planning.
    """
    instructions = (
        "You are the Planner Agent. You specialize in building "
        "day-by-day travel itineraries and sequencing activities. "
        'Always return JSON: {"destination":"...","duration":"...","summary":"..."}'
    )
    
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]
    
    response = client.chat.completions.create(
        model="llama3.2",
        messages=messages,
        temperature=0.7,
        tools=tools,  # Can also use web_search
        tool_choice="required"  # Force tool use if needed
    )
    
    # ... tool execution logic ...
    
    return result_content  # JSON string with itinerary
```

#### Budget Agent
```python
def budget_agent(user_prompt):
    """
    Specialist: Cost estimation and budget validation.
    """
    instructions = (
        "You are the Budget Agent. You estimate costs for lodging, "
        "food, transport, and activities. "
        'Always return JSON: {"cost":"string"}'
    )
    # Similar structure to planner_agent
    ...
    return cost_json
```

#### Local Guide Agent
```python
def local_guide_agent(user_prompt):
    """
    Specialist: Restaurant recommendations and local tips.
    """
    instructions = (
        "You are the Local Guide Agent. You provide restaurants, "
        "neighborhoods, cultural tips, and local highlights. "
        'Always return JSON: {"tips":"string"}'
    )
    ...
    return tips_json
```

### Orchestrator Implementation

```python
def orchestrator(user_prompt):
    """
    Main coordinator: Calls sub-agents and aggregates results.
    """
    instructions = (
        "You are the Travel Orchestrator. Coordinate specialized agents. "
        "Call agents in order: planner_agent → budget_agent → local_guide_agent. "
        "Return combined JSON with all fields."
    )
    
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]
    
    tool_call_count = 0
    max_calls = 10  # Prevent infinite loops
    
    while message.tool_calls and tool_call_count < max_calls:
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Route to correct agent
            if function_name == "planner_agent":
                result = planner_agent(args['prompt'])
            elif function_name == "budget_agent":
                result = budget_agent(args['prompt'])
            elif function_name == "local_guide_agent":
                result = local_guide_agent(args['prompt'])
            elif function_name == "web_search":
                result = web_search(args['query'])
            
            # Append tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # Continue orchestration
        response = client.chat.completions.create(...)
        tool_call_count += 1
    
    return final_aggregated_json
```

### Execution Trace Example

```
User: "Plan trip to Delhi, late September, 1 week, foodie, show flights/hotels"

Orchestrator: "I'll coordinate planner, budget, and guide agents"

Orchestrator calls: planner_agent("Create 7-day Delhi itinerary")
  → Planner returns: {"destination":"Delhi","duration":"7 days","summary":"Day 1: Red Fort..."}

Orchestrator calls: budget_agent("Estimate costs for 7-day Delhi trip")
  → Budget returns: {"cost":"Flights: $800, Hotels: $500, Total: ~$1500"}

Orchestrator calls: local_guide_agent("Recommend Delhi restaurants for foodies")
  → Guide returns: {"tips":"Karim's for kebabs, Indian Accent for fine dining..."}

Orchestrator: Aggregates all results into single JSON
  → Returns: {"destination":"Delhi","duration":"7 days","summary":"...","cost":"$1500","tips":"Karim's..."}
```

### Key Takeaways
✅ **Separation of concerns** - Each agent has single responsibility  
✅ **Modularity** - Easy to add/remove agents  
✅ **Scalability** - Sub-agents can themselves orchestrate others  
✅ **Flexibility** - Orchestrator decides execution order dynamically  

---

## Lesson 4: Add Agent Guardrails for Safe Responses

### Learning Objectives
- ✅ Implement input validation before processing
- ✅ Use OpenAI Agents SDK (first time!)
- ✅ Create guardrail agents
- ✅ Handle guardrail tripwires

### Major Shift: Now Using OpenAI Agents SDK

**Before (Lessons 1-3)**: Manual API calls via `client.chat.completions.create()`  
**Now (Lesson 4+)**: SDK abstractions via `Agent` and `Runner`

### SDK Components Introduction

#### Agent Class
```python
from agents import Agent, Runner, ModelSettings

agent = Agent(
    name="Agent Name",                    # Identifier
    model="gpt-5",                        # GPT-4, GPT-5, etc.
    instructions="System prompt",         # Behavior definition
    output_type=PydanticModel,            # Structured output
    model_settings=ModelSettings(...),    # Advanced config
    tools=[...],                          # Available functions
    input_guardrails=[...]                # Validation functions
)
```

#### Runner Class
```python
result = await Runner.run(
    agent,                    # Agent to execute
    "User prompt",           # Input string
    context=dict,            # Shared context across agents
    session=session          # Persistent state (Lesson 5)
)

output = result.final_output_as(PydanticModel)
```

### Guardrail Implementation

#### Step 1: Define Validation Output Model
```python
class BudgetCheckOutput(BaseModel):
    """
    Output from budget validation guardrail.
    """
    is_valid: bool         # True if budget is realistic
    reasoning: str         # Explanation of decision
```

#### Step 2: Create Guardrail Agent
```python
budget_guardrail_agent = Agent(
    name="Budget Guardrail",
    instructions=(
        "Decide if the user's travel request includes an unrealistic budget. "
        "If request says '10 days in Caribbean for $200' or obviously too low, "
        "set is_valid to False and explain why. "
        "Otherwise set is_valid to True."
    ),
    output_type=BudgetCheckOutput,
)
```

**Purpose**: Specialized agent just for validation.

#### Step 3: Define Guardrail Function
```python
async def budget_guardrail(ctx, agent, input_data):
    """
    Validation function called before main agent processes input.
    
    Args:
        ctx: Context object with shared data
        agent: Main agent being guarded
        input_data: User's input string
    
    Returns:
        GuardrailFunctionOutput with tripwire status
    """
    # Run validation agent
    result = await Runner.run(
        budget_guardrail_agent, 
        input_data, 
        context=ctx.context
    )
    
    final_output = result.final_output_as(BudgetCheckOutput)
    print("Budget guardrail reasoning:", final_output.reasoning)
    
    # Return validation result
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_valid  # True = block request
    )
```

#### Step 4: Attach Guardrail to Main Agent
```python
travel_agent = Agent(
    name="Travel Agent",
    model="gpt-5",
    instructions="...",
    output_type=TravelOutput,
    tools=[...],
    input_guardrails=[
        InputGuardrail(guardrail_function=budget_guardrail)  # ⭐ Attach here
    ]
)
```

#### Step 5: Handle Guardrail Exceptions
```python
async def main():
    try:
        result = await Runner.run(
            travel_agent, 
            "7-day Jamaica trip for $100"  # Unrealistic budget
        )
        print_fields(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("\\nGuardrail blocked this budget:", e)
    except Exception as e:
        print("Error:", e)
```

### Execution Flow with Guardrails

```
User Input: "7-day Jamaica trip for $100"
    ↓
InputGuardrail: budget_guardrail()
    ↓
budget_guardrail_agent runs
    ↓
Output: {"is_valid": false, "reasoning": "$100 for 7 days in Caribbean is unrealistic..."}
    ↓
tripwire_triggered = True
    ↓
Raise InputGuardrailTripwireTriggered
    ↓
❌ Request BLOCKED (never reaches travel_agent)
    ↓
User sees: "Guardrail blocked this budget: ..."
```

**Valid Budget Flow**:
```
User Input: "7-day Jamaica trip for $3000"
    ↓
budget_guardrail() → is_valid=True
    ↓
✅ Request PASSES to travel_agent
    ↓
travel_agent processes normally
```

### Key Takeaways
✅ **Guardrails run BEFORE main agent** - Save costs, prevent bad inputs  
✅ **Guardrails are agents themselves** - Can use LLM reasoning  
✅ **Tripwires block execution** - Clear control flow  
✅ **SDK abstracts complexity** - No manual message management  

---

## Lesson 5: Maintain Agent Context with Sessions

### Learning Objectives
- ✅ Implement conversation memory
- ✅ Persist state across multiple agent runs
- ✅ Use SQLite sessions
- ✅ Build contextual multi-turn conversations

### Session Concept

**Problem**: Each `Runner.run()` starts fresh (no memory of previous turns)

**Solution**: Sessions store message history and context

### Session Implementation

#### Step 1: Import Session
```python
from agents import SQLiteSession
```

#### Step 2: Create Session Instance
```python
session = SQLiteSession("travel_agent_123")  # Session ID (user-specific)
```

**Storage**: In-memory SQLite database (or persistent file)

#### Step 3: First Turn with Session
```python
result = await Runner.run(
    travel_agent,
    "Trip to Jamaica, late September, week-long, $3000 budget",
    session=session  # ⭐ Attach session
)

print_fields(result.final_output)
# Output: Plan for Jamaica with $3000 budget
```

**What Happens**:
- User message saved to session
- Agent response saved to session
- Session persists in database

#### Step 4: Second Turn (Context Remembered)
```python
result = await Runner.run(
    travel_agent,
    "Change to Bahamas instead",  # No need to repeat budget!
    session=session  # Same session
)

print_fields(result.final_output)
# Output: Updated plan for Bahamas with SAME $3000 budget
```

**What Happens**:
- Session loads previous messages
- Agent sees full conversation history
- Agent remembers $3000 budget from Turn 1
- User doesn't need to repeat details

### Session Data Structure

```python
session = {
    "session_id": "travel_agent_123",
    "messages": [
        {"role": "user", "content": "Trip to Jamaica, $3000"},
        {"role": "assistant", "content": "{\"destination\":\"Jamaica\",...}"},
        {"role": "user", "content": "Change to Bahamas"},
        {"role": "assistant", "content": "{\"destination\":\"Bahamas\",...}"}
    ],
    "context": {
        # Custom key-value data shared across turns
    },
    "created_at": "2025-12-29T10:00:00Z",
    "updated_at": "2025-12-29T10:05:00Z"
}
```

### Multi-Turn Conversation Example

```
Turn 1:
User: "Trip to Jamaica, late September, $3000"
Agent: [Plans Jamaica trip with $3000 budget]

Turn 2:
User: "Change to Bahamas"
Agent: [Updates to Bahamas, KEEPS $3000 budget from Turn 1]

Turn 3:
User: "Add snorkeling recommendations"
Agent: [Adds snorkeling to Bahamas plan, still aware of $3000 budget]

Turn 4:
User: "What was my original destination?"
Agent: "Your original destination was Jamaica before switching to Bahamas."
```

### Session Lifecycle

```python
# Create or load session
session = SQLiteSession("user_123")

# Use in multiple runs
result1 = await Runner.run(agent, "Request 1", session=session)
result2 = await Runner.run(agent, "Request 2", session=session)
result3 = await Runner.run(agent, "Request 3", session=session)

# Session automatically persists between runs

# Clear session (optional)
# session.clear()  # Remove all messages

# Session persists until:
# 1. Explicit deletion
# 2. Database file deleted (if file-based)
# 3. Process ends (if in-memory)
```

### Key Takeaways
✅ **Sessions enable multi-turn conversations**  
✅ **Context persists automatically** - No manual message management  
✅ **User experience improves** - No need to repeat information  
✅ **Production-ready pattern** - SQLite can be file-based or in-memory  

---

## Summary Comparison

| Feature | L1 | L2 | L3 | L4 | L5 |
|---------|----|----|----|----|-----|
| **Agent Creation** | Manual API | Manual API | Manual API | Agent SDK | Agent SDK |
| **Tools** | ❌ | ✅ Web Search | ✅ Multiple | ✅ Built-in | ✅ Built-in |
| **Multi-Agent** | ❌ | ❌ | ✅ Orchestration | ✅ Handoffs | ✅ Handoffs |
| **Guardrails** | ❌ | ❌ | ❌ | ✅ Budget Check | ✅ Budget Check |
| **Sessions** | ❌ | ❌ | ❌ | ❌ | ✅ SQLite |
| **Async Execution** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Model** | Llama 3.2 | Llama 3.2 | Llama 3.2 | GPT-5 | GPT-5 |
| **Complexity** | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Next Steps

- **Patterns**: [05_AGENT_PATTERNS.md](./05_AGENT_PATTERNS.md)
- **API Reference**: [07_API_REFERENCE.md](./07_API_REFERENCE.md)
- **Production**: [12_PRODUCTIONIZATION_GUIDE.md](./12_PRODUCTIONIZATION_GUIDE.md)

---

**Document Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**Target Audience**: Developers learning the codebase
