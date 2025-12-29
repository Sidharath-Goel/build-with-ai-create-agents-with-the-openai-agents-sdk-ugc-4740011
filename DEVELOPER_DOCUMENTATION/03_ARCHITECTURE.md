# Architecture Guide - System Design Deep Dive

This document provides a comprehensive architectural overview of the OpenAI Agents SDK travel planning system, including design patterns, data flow, and component interactions.

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Design Patterns](#design-patterns)
5. [Evolution Across Lessons](#evolution-across-lessons)
6. [Production Architecture](#production-architecture)

---

## System Architecture Overview

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                  (Terminal / API / Web App)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Travel Agent (Main Orchestrator)            │   │
│  │  - Receives user requests                                │   │
│  │  - Delegates to specialized agents                       │   │
│  │  - Aggregates results                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Planner Agent  │ │  Budget Agent   │ │ Local Guide     │
│                 │ │                 │ │ Agent           │
│ - Itinerary     │ │ - Cost          │ │ - Restaurants   │
│ - Schedule      │ │   estimation    │ │ - Local tips    │
│ - Activities    │ │ - Budget check  │ │ - Culture       │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        TOOLS LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ WebSearchTool│  │ Custom Tools │  │ Agent-as-Tool│          │
│  │ (DuckDuckGo) │  │              │  │  (Handoffs)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SAFETY LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ Input        │  │ Output       │                             │
│  │ Guardrails   │  │ Validation   │                             │
│  └──────────────┘  └──────────────┘                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ SQLite       │  │ Session      │                             │
│  │ Sessions     │  │ Context      │                             │
│  └──────────────┘  └──────────────┘                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LLM PROVIDER LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ OpenAI API   │  │ Ollama       │  │ Other LLMs   │          │
│  │ (GPT-4/5)    │  │ (Llama 3.2)  │  │ (Future)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Agent Component

**Purpose**: Core decision-making and task execution unit

#### Class Structure
```python
class Agent:
    """
    Represents an AI agent with specific capabilities and instructions.
    """
    def __init__(
        self,
        name: str,                          # Agent identifier
        model: str,                         # LLM model (gpt-4, gpt-5)
        instructions: str,                  # System prompt
        output_type: Type[BaseModel],       # Pydantic model for structured output
        model_settings: ModelSettings,      # Reasoning configuration
        tools: List[Tool],                  # Available functions
        input_guardrails: List[InputGuardrail],  # Safety checks
        handoff_description: str            # When to delegate to this agent
    ):
        ...
```

#### Agent Lifecycle
```
1. Initialization
   ├── Load instructions
   ├── Configure model settings
   ├── Register tools
   └── Setup guardrails

2. Execution (via Runner)
   ├── Receive user input
   ├── Apply input guardrails
   ├── Send to LLM (OpenAI API)
   ├── Process tool calls (if any)
   ├── Validate output
   └── Return structured result

3. Tool Execution (Optional)
   ├── Parse tool call request
   ├── Execute tool function
   ├── Return result to LLM
   └── Continue reasoning

4. Output Generation
   ├── Receive final response from LLM
   ├── Parse JSON output
   ├── Validate against Pydantic model
   └── Return to caller
```

### 2. Runner Component

**Purpose**: Async execution engine for agents

```python
class Runner:
    """
    Executes agents asynchronously with context and session management.
    """
    @staticmethod
    async def run(
        agent: Agent,
        prompt: str,
        context: dict = None,       # Shared context across agents
        session: Session = None     # Persistent conversation state
    ) -> RunResult:
        """
        Execute agent with given input and return structured result.
        """
        ...

class RunResult:
    """
    Contains execution results and metadata.
    """
    final_output: Union[str, BaseModel]  # Final agent output
    messages: List[dict]                 # Conversation history
    tool_calls: List[ToolCall]          # Tools that were executed
    
    def final_output_as(self, model_class: Type[BaseModel]) -> BaseModel:
        """Parse final output as Pydantic model."""
        ...
```

#### Execution Flow
```
await Runner.run(agent, prompt)
    │
    ├─► Validate input
    ├─► Apply input guardrails
    ├─► Build message context
    │   ├─► Load session history (if exists)
    │   └─► Add user message
    │
    ├─► Call LLM API
    │   └─► POST to OpenAI /chat/completions
    │
    ├─► Process response
    │   ├─► Check for tool calls
    │   │   ├─► Execute tools
    │   │   └─► Loop back to LLM
    │   └─► Extract final output
    │
    ├─► Validate output structure
    │   └─► Parse as Pydantic model
    │
    ├─► Save to session (if enabled)
    └─► Return RunResult
```

### 3. Tool Component

**Purpose**: External function integration for agents

#### Tool Types

##### Type 1: Python Function Tool
```python
from agents import tool

@tool
def web_search(query: str) -> str:
    """
    Search the web for information.
    
    Args:
        query: Search query string
    
    Returns:
        Search results as string
    """
    # Implementation
    return results

# Used in agent:
agent = Agent(
    tools=[web_search, ...]
)
```

##### Type 2: Agent-as-Tool (Handoffs)
```python
sub_agent = Agent(
    name="Sub Agent",
    handoff_description="When to use this agent",
    ...
)

main_agent = Agent(
    tools=[
        sub_agent.as_tool(
            tool_name="sub_agent",
            tool_description="Delegates specific task"
        )
    ]
)
```

##### Type 3: Built-in Tools
```python
from agents import WebSearchTool, FileReadTool

agent = Agent(
    tools=[
        WebSearchTool(),      # Web search via Bing/DuckDuckGo
        FileReadTool(),       # Read files from filesystem
    ]
)
```

#### Tool Execution Flow
```
1. LLM requests tool call
   └─► Returns: {"tool_calls": [{"function": {"name": "web_search", "arguments": "{\"query\":\"Paris\"}"}}]}

2. Runner intercepts tool call
   ├─► Parse function name
   ├─► Parse arguments (JSON)
   └─► Execute Python function

3. Tool executes and returns result
   └─► web_search("Paris") → "Paris is the capital of France..."

4. Result sent back to LLM
   └─► Append to message history:
       {"role": "tool", "tool_call_id": "...", "content": "Paris is..."}

5. LLM continues reasoning
   └─► May call more tools or return final output
```

### 4. Guardrail Component

**Purpose**: Input validation and safety checks

```python
from agents import InputGuardrail, GuardrailFunctionOutput

# Define validation agent
budget_guardrail_agent = Agent(
    name="Budget Validator",
    instructions="Check if budget is realistic",
    output_type=BudgetCheckOutput
)

# Define guardrail function
async def budget_guardrail(ctx, agent, input_data):
    """
    Validate budget before processing request.
    """
    result = await Runner.run(
        budget_guardrail_agent, 
        input_data, 
        context=ctx.context
    )
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_valid  # Block if invalid
    )

# Attach to agent
agent = Agent(
    input_guardrails=[
        InputGuardrail(guardrail_function=budget_guardrail)
    ]
)
```

#### Guardrail Execution Flow
```
User Input → Guardrail Check → Agent Processing
                  │
                  ├─► Valid → Continue
                  │
                  └─► Invalid → Raise InputGuardrailTripwireTriggered
                                Block request
                                Return error to user
```

### 5. Session Component

**Purpose**: Conversation state persistence

```python
from agents import SQLiteSession

# Create session
session = SQLiteSession("user_123")

# First turn
result1 = await Runner.run(agent, "Plan trip to Paris", session=session)

# Second turn - agent remembers context
result2 = await Runner.run(agent, "Change destination to London", session=session)
```

#### Session Storage Structure
```sql
-- SQLite database schema
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    messages TEXT,          -- JSON array of message history
    context TEXT,           -- JSON object of shared context
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Session Lifecycle
```
1. Session Creation
   └─► SQLiteSession("session_id") → Creates or loads from DB

2. Message History Management
   ├─► Load previous messages on agent run
   ├─► Append new user message
   ├─► Append agent response
   └─► Save to database

3. Context Sharing
   ├─► Store key-value pairs
   ├─► Accessible across agent calls
   └─► Persist between runs

4. Session Cleanup
   └─► Automatic or manual deletion
```

---

## Data Flow Diagrams

### Lesson 1: Basic Agent Data Flow

```
User Input
    │
    ▼
┌─────────────────┐
│   main()        │
│  function       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OpenAI API      │
│ client.chat.    │
│ completions.    │
│ create()        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OpenAI Server   │
│ (GPT-4/Llama)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ JSON Response   │
│ {"destination": │
│  "...", ...}    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ print_fields()  │
│ Parse & Display │
└─────────────────┘
```

### Lesson 3: Multi-Agent Orchestration Flow

```
User: "Plan trip to Delhi"
    │
    ▼
┌──────────────────────────────┐
│ Orchestrator Agent           │
│ - Analyze request            │
│ - Determine agent sequence   │
└────────────┬─────────────────┘
             │
     ┌───────┴───────┬──────────────┐
     ▼               ▼              ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ Planner │   │ Budget  │   │ Guide   │
│ Agent   │   │ Agent   │   │ Agent   │
└────┬────┘   └────┬────┘   └────┬────┘
     │             │             │
     │ Itinerary   │ Cost        │ Tips
     │             │             │
     └─────────────┴─────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Orchestrator    │
         │ Aggregates      │
         │ All Results     │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Final Output    │
         │ (Combined JSON) │
         └─────────────────┘
```

### Lesson 4: Guardrail Flow

```
User Input: "Trip for $100"
    │
    ▼
┌──────────────────────┐
│ Input Guardrail      │
│ (Budget Validator)   │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│ Valid  │   │Invalid │
└───┬────┘   └───┬────┘
    │            │
    ▼            ▼
Continue    Raise Exception
    │         (Block Request)
    ▼
┌──────────────────────┐
│ Travel Agent         │
│ (Main Processing)    │
└──────────────────────┘
```

### Lesson 5: Session Flow

```
Turn 1: "Trip to Jamaica, $3000"
    │
    ▼
┌──────────────────────┐
│ Runner.run()         │
│ session=session      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Travel Agent         │
│ (No prior context)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Save to Session DB   │
│ - User message       │
│ - Agent response     │
└──────────────────────┘

Turn 2: "Change to Bahamas"
    │
    ▼
┌──────────────────────┐
│ Runner.run()         │
│ session=session      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Load Session Context │
│ - Previous messages  │
│ - Remembers $3000    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Travel Agent         │
│ (With context)       │
│ Knows budget from T1 │
└──────────────────────┘
```

---

## Design Patterns

### 1. Agent Orchestration Pattern

**Problem**: Complex tasks require multiple specialized capabilities  
**Solution**: Delegate subtasks to specialized agents

```python
# Main orchestrator agent
orchestrator = Agent(
    name="Orchestrator",
    tools=[
        specialist_1.as_tool(),
        specialist_2.as_tool(),
        specialist_3.as_tool()
    ]
)

# Execution delegates to specialists based on task
result = await Runner.run(orchestrator, user_request)
```

**Benefits**:
- ✅ Separation of concerns
- ✅ Modular agent capabilities
- ✅ Easier testing and maintenance
- ✅ Reusable specialist agents

### 2. Tool Abstraction Pattern

**Problem**: Agents need external data/functionality  
**Solution**: Wrap functions as tools with clear interfaces

```python
@tool
def external_api(param: str) -> dict:
    """Tool docstring becomes description for LLM"""
    return call_api(param)

agent = Agent(tools=[external_api])
```

**Benefits**:
- ✅ Clean agent-tool interface
- ✅ LLM understands when to call tools
- ✅ Type-safe function signatures
- ✅ Testable in isolation

### 3. Structured Output Pattern

**Problem**: LLM outputs are unpredictable text  
**Solution**: Use Pydantic models to enforce structure

```python
class TravelOutput(BaseModel):
    destination: str
    duration: str
    summary: str

agent = Agent(
    output_type=TravelOutput,
    instructions="Return JSON matching TravelOutput schema"
)

result = await Runner.run(agent, prompt)
output: TravelOutput = result.final_output  # Guaranteed type
```

**Benefits**:
- ✅ Type safety
- ✅ Validation at runtime
- ✅ Predictable outputs
- ✅ Easy serialization

### 4. Guardrail Pattern

**Problem**: Unsafe or invalid inputs need filtering  
**Solution**: Pre-process inputs with validation agents

```python
async def validator(ctx, agent, input_data):
    is_valid = await check_safety(input_data)
    return GuardrailFunctionOutput(
        tripwire_triggered=not is_valid
    )

agent = Agent(
    input_guardrails=[InputGuardrail(guardrail_function=validator)]
)
```

**Benefits**:
- ✅ Safety layer before processing
- ✅ Prevent invalid requests
- ✅ Cost savings (block bad requests early)
- ✅ Composable validators

### 5. Session Pattern

**Problem**: Agents need conversation memory  
**Solution**: Persist message history across turns

```python
session = SQLiteSession("user_id")

# Multi-turn conversation
await Runner.run(agent, "First request", session=session)
await Runner.run(agent, "Follow-up request", session=session)
```

**Benefits**:
- ✅ Contextual responses
- ✅ Multi-turn conversations
- ✅ User-specific state
- ✅ Persistent storage

---

## Evolution Across Lessons

### Lesson 1 → 2: Adding Tools
```
Basic Agent              →    Agent + Tools
(Static knowledge)            (Live data access)

Instructions only        →    Instructions + WebSearchTool
```

### Lesson 2 → 3: Multi-Agent
```
Single Agent            →    Orchestrator + Specialists
(One capability)             (Multiple capabilities)

Monolithic              →    Modular architecture
```

### Lesson 3 → 4: Guardrails
```
No validation           →    Input validation
(Accept all inputs)          (Filter unsafe inputs)

Direct processing       →    Guardrail → Processing
```

### Lesson 4 → 5: Sessions
```
Stateless               →    Stateful
(Each request isolated)      (Remembers context)

No memory               →    SQLite persistence
```

---

## Production Architecture

### Enhanced Production System

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ADDITIONS                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Load         │  │ Rate         │  │ Monitoring   │          │
│  │ Balancer     │  │ Limiting     │  │ & Logging    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
         [ Existing Agent Architecture ]
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 PRODUCTION ENHANCEMENTS                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Redis        │  │ PostgreSQL   │  │ Distributed  │          │
│  │ Caching      │  │ Sessions     │  │ Tracing      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Production Enhancements
1. **API Gateway**: FastAPI/Flask wrapper
2. **Caching**: Redis for frequent queries
3. **Database**: PostgreSQL for production sessions
4. **Monitoring**: Prometheus + Grafana
5. **Logging**: Structured logging (JSON)
6. **Security**: API key rotation, rate limiting
7. **Scaling**: Horizontal pod autoscaling (K8s)

---

## Next Steps

- **Implementation**: [06_LESSON_BY_LESSON_GUIDE.md](./06_LESSON_BY_LESSON_GUIDE.md)
- **API Details**: [07_API_REFERENCE.md](./07_API_REFERENCE.md)
- **Production**: [12_PRODUCTIONIZATION_GUIDE.md](./12_PRODUCTIONIZATION_GUIDE.md)

---

**Document Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**Target Audience**: Solution Architects, Senior Engineers
