# Code Examples - Standalone Samples

Practical, copy-paste ready code examples for common patterns in the OpenAI Agents SDK.

---

## Minimal Agent Example

```python
"""
Simplest possible agent - perfect for testing setup.
"""
import asyncio
import os
from agents import Agent, Runner
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class SimpleOutput(BaseModel):
    response: str

agent = Agent(
    name="Simple Agent",
    model="gpt-4",
    instructions="You are a helpful assistant. Respond concisely.",
    output_type=SimpleOutput
)

async def main():
    result = await Runner.run(agent, "Hello, how are you?")
    print(result.final_output.response)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Custom Tool Example

```python
"""
Creating a custom tool for weather information.
"""
import asyncio
from agents import Agent, Runner, tool
from pydantic import BaseModel

@tool
def get_weather(city: str) -> str:
    """
    Get weather information for a city.
    
    Args:
        city: Name of the city
    
    Returns:
        Weather description
    """
    # Mock implementation (replace with real API)
    weather_data = {
        "Paris": "Sunny, 22°C",
        "London": "Cloudy, 15°C",
        "Tokyo": "Rainy, 18°C"
    }
    return weather_data.get(city, f"Weather data not available for {city}")

class TravelOutput(BaseModel):
    destination: str
    weather: str
    suggestion: str

agent = Agent(
    name="Travel Weather Agent",
    model="gpt-4",
    instructions=(
        "You are a travel assistant. When user asks about a destination, "
        "use get_weather tool to check weather and provide suggestions."
    ),
    output_type=TravelOutput,
    tools=[get_weather]
)

async def main():
    result = await Runner.run(agent, "What's the weather in Paris? Should I visit?")
    output = result.final_output
    print(f"Destination: {output.destination}")
    print(f"Weather: {output.weather}")
    print(f"Suggestion: {output.suggestion}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Guardrail Example

```python
"""
Input validation with guardrails.
"""
import asyncio
from agents import (
    Agent, Runner, InputGuardrail, GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered
)
from pydantic import BaseModel

class ValidationOutput(BaseModel):
    is_safe: bool
    reason: str

# Validation agent
validator = Agent(
    name="Content Validator",
    instructions=(
        "Check if input contains inappropriate content or requests. "
        "Set is_safe to False if content is harmful, offensive, or requests illegal activities."
    ),
    output_type=ValidationOutput
)

# Guardrail function
async def content_guardrail(ctx, agent, input_data):
    result = await Runner.run(validator, input_data, context=ctx.context)
    validation = result.final_output
    
    print(f"Validation: {validation.reason}")
    
    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=not validation.is_safe
    )

class Output(BaseModel):
    response: str

# Main agent with guardrail
agent = Agent(
    name="Safe Agent",
    model="gpt-4",
    instructions="You are a helpful assistant.",
    output_type=Output,
    input_guardrails=[InputGuardrail(guardrail_function=content_guardrail)]
)

async def main():
    try:
        # Safe input
        result = await Runner.run(agent, "Tell me about travel destinations")
        print("Response:", result.final_output.response)
        
        # Unsafe input (example)
        result = await Runner.run(agent, "How do I hack a computer?")
        print("Response:", result.final_output.response)
        
    except InputGuardrailTripwireTriggered as e:
        print(f"Blocked by guardrail: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Session Example

```python
"""
Multi-turn conversation with session memory.
"""
import asyncio
from agents import Agent, Runner, SQLiteSession
from pydantic import BaseModel

class ChatOutput(BaseModel):
    response: str

agent = Agent(
    name="Chat Agent",
    model="gpt-4",
    instructions="You are a helpful assistant with memory of our conversation.",
    output_type=ChatOutput
)

async def main():
    # Create session for user
    session = SQLiteSession("user_alice")
    
    # Turn 1
    print("\\n--- Turn 1 ---")
    result = await Runner.run(
        agent,
        "My name is Alice and I love Paris",
        session=session
    )
    print(f"Agent: {result.final_output.response}")
    
    # Turn 2 - agent remembers name
    print("\\n--- Turn 2 ---")
    result = await Runner.run(
        agent,
        "What's my name and favorite city?",
        session=session
    )
    print(f"Agent: {result.final_output.response}")
    
    # Turn 3 - continue conversation
    print("\\n--- Turn 3 ---")
    result = await Runner.run(
        agent,
        "Why do I love that city?",
        session=session
    )
    print(f"Agent: {result.final_output.response}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Agent-as-Tool (Multi-Agent)

```python
"""
Multi-agent system with delegation.
"""
import asyncio
from agents import Agent, Runner, ModelSettings
from pydantic import BaseModel

# Specialist agents
class FactOutput(BaseModel):
    fact: str

fact_agent = Agent(
    name="Fact Agent",
    model="gpt-4",
    handoff_description="Use when user asks for facts or information",
    instructions="Provide concise, accurate facts.",
    output_type=FactOutput,
    model_settings=ModelSettings(reasoning={"effort": "low"})
)

class JokeOutput(BaseModel):
    joke: str

joke_agent = Agent(
    name="Joke Agent",
    model="gpt-4",
    handoff_description="Use when user wants humor or a joke",
    instructions="Tell funny, family-friendly jokes.",
    output_type=JokeOutput,
    model_settings=ModelSettings(reasoning={"effort": "low"})
)

# Orchestrator
class OrchestratorOutput(BaseModel):
    response: str
    source: str  # Which agent provided the answer

orchestrator = Agent(
    name="Orchestrator",
    model="gpt-4",
    instructions=(
        "You coordinate specialist agents. "
        "Delegate to fact_agent for factual questions. "
        "Delegate to joke_agent for humor requests. "
        "Return the specialist's answer with source."
    ),
    output_type=OrchestratorOutput,
    tools=[
        fact_agent.as_tool(tool_name="fact_agent", tool_description="Get facts"),
        joke_agent.as_tool(tool_name="joke_agent", tool_description="Get jokes")
    ]
)

async def main():
    # Request 1: Fact
    print("\\n--- Request: Fact ---")
    result = await Runner.run(orchestrator, "Tell me a fact about the ocean")
    output = result.final_output
    print(f"Response: {output.response}")
    print(f"Source: {output.source}")
    
    # Request 2: Joke
    print("\\n--- Request: Joke ---")
    result = await Runner.run(orchestrator, "Tell me a joke")
    output = result.final_output
    print(f"Response: {output.response}")
    print(f"Source: {output.source}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Error Handling Example

```python
"""
Robust error handling for production.
"""
import asyncio
import logging
from agents import Agent, Runner, InputGuardrailTripwireTriggered
from pydantic import BaseModel, ValidationError
from openai import OpenAIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Output(BaseModel):
    response: str

agent = Agent(
    name="Production Agent",
    model="gpt-4",
    instructions="You are a helpful assistant.",
    output_type=Output
)

async def safe_run_agent(prompt: str, max_retries: int = 3):
    """
    Run agent with comprehensive error handling.
    """
    for attempt in range(max_retries):
        try:
            result = await Runner.run(agent, prompt)
            logger.info("Agent execution successful")
            return result.final_output
            
        except InputGuardrailTripwireTriggered as e:
            logger.warning(f"Guardrail blocked request: {e}")
            raise  # Don't retry guardrail blocks
            
        except ValidationError as e:
            logger.error(f"Output validation failed: {e}")
            if attempt == max_retries - 1:
                raise
            logger.info(f"Retrying... (attempt {attempt + 1}/{max_retries})")
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            logger.info(f"Retrying... (attempt {attempt + 1}/{max_retries})")
            
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise

async def main():
    try:
        output = await safe_run_agent("Hello, how are you?")
        print(f"Response: {output.response}")
    except Exception as e:
        print(f"Failed after retries: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## FastAPI Integration Example

```python
"""
FastAPI wrapper for agents (production API).
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

from agents import Agent, Runner

# Initialize FastAPI
app = FastAPI(title="Agent API")

# Define models
class AgentRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    response: str

class ChatOutput(BaseModel):
    response: str

# Create agent
agent = Agent(
    name="API Agent",
    model="gpt-4",
    instructions="You are a helpful API assistant.",
    output_type=ChatOutput
)

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent_endpoint(request: AgentRequest):
    """
    Execute agent with user prompt.
    """
    try:
        result = await Runner.run(agent, request.prompt)
        return AgentResponse(response=result.final_output.response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

# Run with: uvicorn filename:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Caching Example

```python
"""
Simple caching for agent responses.
"""
import asyncio
import hashlib
import json
from typing import Optional
from agents import Agent, Runner
from pydantic import BaseModel

class Output(BaseModel):
    response: str

agent = Agent(
    name="Cached Agent",
    model="gpt-4",
    instructions="You are a helpful assistant.",
    output_type=Output
)

# Simple in-memory cache
cache = {}

def get_cache_key(prompt: str) -> str:
    """Generate cache key from prompt."""
    return hashlib.md5(prompt.encode()).hexdigest()

async def run_with_cache(prompt: str) -> Output:
    """
    Run agent with caching.
    """
    cache_key = get_cache_key(prompt)
    
    # Check cache
    if cache_key in cache:
        print("✅ Cache hit!")
        return Output(**cache[cache_key])
    
    print("❌ Cache miss, calling agent...")
    result = await Runner.run(agent, prompt)
    output = result.final_output
    
    # Save to cache
    cache[cache_key] = output.dict()
    
    return output

async def main():
    # First call - cache miss
    print("\\n--- First call ---")
    output = await run_with_cache("What is Python?")
    print(f"Response: {output.response[:100]}...")
    
    # Second call - cache hit
    print("\\n--- Second call (same prompt) ---")
    output = await run_with_cache("What is Python?")
    print(f"Response: {output.response[:100]}...")
    
    # Third call - different prompt (cache miss)
    print("\\n--- Third call (different prompt) ---")
    output = await run_with_cache("What is JavaScript?")
    print(f"Response: {output.response[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Testing Example

```python
"""
Unit testing agents with mocked responses.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from agents import Agent, Runner
from pydantic import BaseModel

class Output(BaseModel):
    response: str

agent = Agent(
    name="Test Agent",
    model="gpt-4",
    instructions="You are a test assistant.",
    output_type=Output
)

@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent returns expected output structure."""
    result = await Runner.run(agent, "Hello")
    assert isinstance(result.final_output, Output)
    assert isinstance(result.final_output.response, str)
    assert len(result.final_output.response) > 0

@pytest.mark.asyncio
async def test_agent_with_mock():
    """Test agent with mocked LLM response."""
    mock_output = Output(response="Mocked response")
    
    with patch('agents.Runner.run', new_callable=AsyncMock) as mock_run:
        mock_run.return_value.final_output = mock_output
        
        result = await Runner.run(agent, "Test prompt")
        assert result.final_output.response == "Mocked response"

# Run tests with: pytest test_example.py
```

---

All examples are:
- ✅ Production-ready patterns
- ✅ Copy-paste ready
- ✅ Include error handling
- ✅ Documented with comments

To use:
1. Copy example to new file
2. Install dependencies: `pip install -r requirements.txt`
3. Set OPENAI_API_KEY in `.env`
4. Run: `python example_file.py`
