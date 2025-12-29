# Code Structure - File Organization & Dependencies

Complete breakdown of the project's file structure, module relationships, and code organization patterns.

---

## Project Directory Tree

```
build-with-ai-create-agents-with-the-openai-agents-sdk-ugc-4740011/
│
├── .devcontainer/                    # GitHub Codespaces configuration
│   └── devcontainer.json
│
├── .github/                          # GitHub workflows and settings
│   └── copilot-instructions.md       # AI assistant guidelines
│
├── .vscode/                          # VS Code workspace settings
│   ├── settings.json
│   └── launch.json (create manually)
│
├── 1 Create the Core Travel Agent/  # LESSON 1: Basic agent
│   ├── agent.py                     # ⭐ Main implementation
│   └── OPENAI__agent.py             # OpenAI-specific variant
│
├── 2 Extend the Agent with Tools/   # LESSON 2: Tool integration
│   ├── agent.py                     # ⭐ With web_search tool
│   └── OPENAI__agent.py             # OpenAI variant
│
├── 3 Orchestrate Mulitple Agents/   # LESSON 3: Multi-agent system
│   ├── agent.py                     # ⭐ Orchestrator pattern
│   └── OPENAI_agent.py              # OpenAI variant
│
├── 4 Add Agent Guardrails for Safe Responses/  # LESSON 4: Safety
│   └── agent.py                     # ⭐ With budget guardrails
│
├── 5 Maintain Agent Context with Sessions/     # LESSON 5: State
│   └── agent.py                     # ⭐ With SQLite sessions
│
├── INSTRUCTOR_INSTRUCTIONS/         # Course setup documentation
│   ├── README.md                    # Instructor guide
│   └── devcontainer-examples/       # Example configurations
│       ├── go-cli/
│       ├── php/
│       ├── python/
│       └── web/
│
├── DEVELOPER_DOCUMENTATION/          # ⭐ THIS FOLDER - Production docs
│   ├── 00_PROJECT_OVERVIEW.md
│   ├── 01_QUICK_START.md
│   ├── 02_ENVIRONMENT_SETUP.md
│   ├── 03_ARCHITECTURE.md
│   ├── 04_CODE_STRUCTURE.md        # ⭐ YOU ARE HERE
│   ├── 05_AGENT_PATTERNS.md
│   ├── 06_LESSON_BY_LESSON_GUIDE.md
│   ├── 07_API_REFERENCE.md
│   ├── 08_TOOLS_AND_INTEGRATIONS.md
│   ├── 09_GUARDRAILS_AND_SAFETY.md
│   ├── 10_SESSIONS_AND_CONTEXT.md
│   ├── 11_TESTING_STRATEGY.md
│   ├── 12_PRODUCTIONIZATION_GUIDE.md
│   ├── 13_TROUBLESHOOTING.md
│   ├── 14_EXTENDING_THE_PROJECT.md
│   ├── 15_GLOSSARY.md
│   ├── DIAGRAMS/
│   └── CODE_EXAMPLES/
│
├── .env                              # ⚠️ Environment variables (not in git)
├── .gitignore                        # Git ignore patterns
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # License agreement
├── NOTICE                            # Third-party dependencies
├── README.md                         # Main project README
├── requirements.txt                  # Python dependencies
├── course_image.png                  # Course thumbnail
└── venv/                             # Virtual environment (not in git)
```

---

## File-by-File Breakdown

### Root Configuration Files

#### `requirements.txt`
**Purpose**: Python dependency specification  
**Content**:
```txt
openai==2.6.1          # OpenAI Python client
python-dotenv          # Environment variable loading
openai-agents          # OpenAI Agents SDK
fastapi                # Web framework (optional)
pydantic               # Data validation
requests               # HTTP client for tools
```

**Used By**: pip during installation  
**Modify When**: Adding new Python dependencies

#### `.env`
**Purpose**: Store sensitive API keys and configuration  
**Content Example**:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

**⚠️ Security**: NEVER commit to git (in `.gitignore`)  
**Used By**: `python-dotenv` package via `load_dotenv()`

#### `.gitignore`
**Purpose**: Exclude files from version control  
**Key Patterns**:
```
venv/                  # Virtual environment
.env                   # API keys
__pycache__/          # Python cache
*.pyc                 # Compiled Python
.DS_Store             # macOS system files
```

---

## Lesson Code Files

### Lesson 1: `1 Create the Core Travel Agent/agent.py`

**Purpose**: Basic agent with structured output  
**Lines of Code**: ~100  
**Complexity**: ⭐ (Beginner)

**Key Components**:
```python
# 1. Imports
import asyncio, json
from openai import OpenAI
from pydantic import BaseModel

# 2. Model Definition
class TravelOutput(BaseModel):
    destination: str
    duration: str
    summary: str

# 3. Agent Instructions
instructions = "You are a travel planner..."

# 4. Execution Logic
def main():
    response = client.chat.completions.create(...)
    print_fields(response)

# 5. Entry Point
if __name__ == "__main__":
    main()
```

**Dependencies**:
- `openai`: For API calls
- `pydantic`: For output validation
- No agent SDK yet (manual API calls)

---

### Lesson 2: `2 Extend the Agent with Tools/agent.py`

**Purpose**: Add web search capability  
**Lines of Code**: ~150  
**Complexity**: ⭐⭐ (Intermediate)

**Key Additions**:
```python
# Tool function
def web_search(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    return response.json()

# Tool definition for LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web",
            "parameters": {...}
        }
    }
]

# Tool execution logic
if message.tool_calls:
    for tool_call in message.tool_calls:
        result = web_search(args['query'])
        # Send result back to LLM
```

**New Dependencies**:
- `requests`: HTTP library for DuckDuckGo API

---

### Lesson 3: `3 Orchestrate Mulitple Agents/agent.py`

**Purpose**: Multi-agent orchestration  
**Lines of Code**: ~348  
**Complexity**: ⭐⭐⭐ (Advanced)

**Architecture**:
```python
# Main orchestrator
def orchestrator(user_prompt):
    # Calls sub-agents via tool mechanism
    ...

# Sub-agent 1: Planner
def planner_agent(user_prompt):
    # Day-by-day itinerary
    ...

# Sub-agent 2: Budget
def budget_agent(user_prompt):
    # Cost estimation
    ...

# Sub-agent 3: Local Guide
def local_guide_agent(user_prompt):
    # Dining & tips
    ...

# Tool definitions for all sub-agents
tools = [
    {"function": {"name": "planner_agent", ...}},
    {"function": {"name": "budget_agent", ...}},
    {"function": {"name": "local_guide_agent", ...}},
]
```

**Key Pattern**: Recursive tool calling (agent calls agent)

---

### Lesson 4: `4 Add Agent Guardrails for Safe Responses/agent.py`

**Purpose**: Input validation and safety  
**Lines of Code**: ~190  
**Complexity**: ⭐⭐⭐ (Advanced)

**Now Using**: OpenAI Agents SDK (first usage!)

**Key Components**:
```python
from agents import (
    Agent, Runner, ModelSettings, WebSearchTool,
    GuardrailFunctionOutput, InputGuardrail
)

# Guardrail agent
budget_guardrail_agent = Agent(
    name="Budget Guardrail",
    output_type=BudgetCheckOutput,
    instructions="Validate budget..."
)

# Guardrail function
async def budget_guardrail(ctx, agent, input_data):
    result = await Runner.run(budget_guardrail_agent, input_data)
    return GuardrailFunctionOutput(
        tripwire_triggered=not result.final_output.is_valid
    )

# Main agent with guardrail
travel_agent = Agent(
    input_guardrails=[InputGuardrail(guardrail_function=budget_guardrail)]
)

# Execution
async def main():
    try:
        result = await Runner.run(travel_agent, prompt)
    except InputGuardrailTripwireTriggered:
        print("Blocked by guardrail")
```

**New SDK Features Used**:
- `Agent` class
- `Runner.run()` async execution
- `ModelSettings` configuration
- Built-in `WebSearchTool`
- Guardrail system

---

### Lesson 5: `5 Maintain Agent Context with Sessions/agent.py`

**Purpose**: Persistent conversation memory  
**Lines of Code**: ~204  
**Complexity**: ⭐⭐⭐⭐ (Expert)

**Key Addition**:
```python
from agents import SQLiteSession

async def main():
    # Create or load session
    session = SQLiteSession("travel_agent_123")
    
    # First turn
    result = await Runner.run(
        travel_agent,
        "Trip to Jamaica, $3000",
        session=session
    )
    
    # Second turn - remembers context
    result = await Runner.run(
        travel_agent,
        "Change to Bahamas instead",  # No need to repeat budget!
        session=session
    )
```

**Session Storage**: SQLite database (in-memory or file-based)

---

## Module Dependencies

### Dependency Graph

```
agent.py
    │
    ├─► openai (2.6.1)
    │   └─► httpx, pydantic, typing-extensions
    │
    ├─► openai-agents
    │   └─► openai, pydantic
    │
    ├─► pydantic
    │   └─► typing-extensions
    │
    ├─► python-dotenv
    │   └─► (no dependencies)
    │
    └─► requests
        └─► urllib3, charset-normalizer
```

### Import Patterns Across Lessons

| Module | Lesson 1 | Lesson 2 | Lesson 3 | Lesson 4 | Lesson 5 |
|--------|----------|----------|----------|----------|----------|
| `openai` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `pydantic` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `requests` | ❌ | ✅ | ✅ | ❌ | ❌ |
| `agents.Agent` | ❌ | ❌ | ❌ | ✅ | ✅ |
| `agents.Runner` | ❌ | ❌ | ❌ | ✅ | ✅ |
| `agents.WebSearchTool` | ❌ | ❌ | ❌ | ✅ | ✅ |
| `agents.SQLiteSession` | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Code Organization Patterns

### Standard File Structure (All Lessons)

```python
"""
Docstring: Lesson description
Prereqs: Setup instructions
"""

# 1. IMPORTS
import standard_library
from third_party import modules
from agents import SDK_components

# 2. CLIENT CONFIGURATION
client = OpenAI(...)

# 3. DATA MODELS
class OutputModel(BaseModel):
    field: type

# 4. AGENT DEFINITIONS
agent = Agent(...)

# 5. TOOL FUNCTIONS
def tool_function(param):
    ...

# 6. HELPER FUNCTIONS
def print_fields(data):
    ...

# 7. MAIN EXECUTION
async def main():
    result = await Runner.run(...)

# 8. ENTRY POINT
if __name__ == "__main__":
    asyncio.run(main())  # or main() for sync
```

### Configuration Pattern

```python
# Environment variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# OpenAI client
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# OR Ollama client (lessons 1-3)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
```

### Error Handling Pattern

```python
try:
    result = await Runner.run(agent, prompt)
    print_fields(result.final_output)
except InputGuardrailTripwireTriggered as e:
    print("Guardrail triggered:", e)
except ValidationError as e:
    print("Output validation failed:", e)
except Exception as e:
    print("General error:", e)
```

---

## Code Metrics

### Lines of Code (LOC) by Lesson

| Lesson | File | LOC | Comments | Functions | Classes |
|--------|------|-----|----------|-----------|---------|
| 1 | agent.py | 100 | 15 | 2 | 1 |
| 2 | agent.py | 150 | 20 | 3 | 1 |
| 3 | agent.py | 348 | 40 | 6 | 1 |
| 4 | agent.py | 190 | 25 | 4 | 3 |
| 5 | agent.py | 204 | 28 | 4 | 3 |

### Complexity Metrics

| Lesson | Cyclomatic Complexity | API Calls | Tool Definitions |
|--------|----------------------|-----------|------------------|
| 1 | Low (3) | 1 | 0 |
| 2 | Medium (7) | 2-3 | 1 |
| 3 | High (15) | 5-10 | 4 |
| 4 | Medium (10) | 2-5 | 3 |
| 5 | Medium (12) | 2-6 | 3 |

---

## Key File Relationships

### Configuration Flow
```
.env → load_dotenv() → os.environ → OpenAI(api_key=...)
```

### Import Chain
```
agent.py
    ↓
openai package
    ↓
openai-agents package
    ↓
pydantic package
```

### Execution Flow
```
agent.py:main()
    ↓
Runner.run(agent, prompt)
    ↓
OpenAI API call
    ↓
Tool execution (optional)
    ↓
Output validation
    ↓
print_fields()
```

---

## Naming Conventions

### Files
- `agent.py` - Main implementation
- `OPENAI__agent.py` - OpenAI API variant (deprecated in later lessons)

### Variables
- `agent` - Agent instance
- `client` - OpenAI client
- `result` - Runner execution result
- `session` - SQLiteSession instance
- `instructions` - System prompt string

### Functions
- `main()` - Entry point (async or sync)
- `print_fields()` - Display helper
- `*_agent()` - Sub-agent functions (Lesson 3)
- `*_guardrail()` - Guardrail functions (Lesson 4+)

### Classes
- `*Output` - Pydantic output models (e.g., `TravelOutput`)
- `Agent` - From SDK
- `Runner` - From SDK

---

## Code Reusability

### Common Patterns to Extract

#### 1. Output Display Helper
```python
# Used in all lessons - candidate for utility module
def print_fields(data):
    if isinstance(data, str):
        try:
            data = OutputModel(**json.loads(data))
        except (json.JSONDecodeError, ValidationError):
            print("Raw output:", data)
            return
    for field, value in data.dict().items():
        print(f"{field.title()}: {value}")
```

#### 2. Client Configuration
```python
# Could be centralized in config.py
def get_client(use_ollama=False):
    if use_ollama:
        return OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
    else:
        load_dotenv(find_dotenv())
        return OpenAI(api_key=os.environ['OPENAI_API_KEY'])
```

#### 3. Error Handling Wrapper
```python
# Reusable across all lessons
async def safe_run_agent(agent, prompt, session=None):
    try:
        result = await Runner.run(agent, prompt, session=session)
        return result.final_output
    except InputGuardrailTripwireTriggered as e:
        logging.warning("Guardrail triggered: %s", e)
        raise
    except ValidationError as e:
        logging.error("Output validation failed: %s", e)
        raise
    except Exception as e:
        logging.error("Agent execution failed: %s", e)
        raise
```

---

## Production Code Structure Recommendations

### Proposed Structure for Production

```
production-agents/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # Base agent configurations
│   │   ├── travel_agent.py      # Main orchestrator
│   │   ├── planner_agent.py     # Itinerary planning
│   │   ├── budget_agent.py      # Cost estimation
│   │   └── guide_agent.py       # Local recommendations
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py        # Search tool
│   │   └── custom_tools.py      # Additional tools
│   │
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── budget_validator.py  # Budget validation
│   │   └── content_filter.py    # Content safety
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic models
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration loading
│   │   ├── logging.py           # Logging setup
│   │   └── helpers.py           # Utility functions
│   │
│   └── api/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       └── routes.py            # API endpoints
│
├── tests/
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_guardrails.py
│
├── config/
│   ├── development.yaml
│   ├── production.yaml
│   └── logging.yaml
│
├── .env.example                  # Template for .env
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Multi-container setup
└── README.md                     # Production README
```

---

## Next Steps

- **Deep Dive**: [06_LESSON_BY_LESSON_GUIDE.md](./06_LESSON_BY_LESSON_GUIDE.md)
- **Patterns**: [05_AGENT_PATTERNS.md](./05_AGENT_PATTERNS.md)
- **Production**: [12_PRODUCTIONIZATION_GUIDE.md](./12_PRODUCTIONIZATION_GUIDE.md)

---

**Document Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**Target Audience**: Code Reviewers, New Developers
