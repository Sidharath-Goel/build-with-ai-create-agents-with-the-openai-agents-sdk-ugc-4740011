"""
Build with AI: Create Agents with the OpenAI Agents SDK
All examples use Python and the OpenAI client.

Prereqs:
  pip install -r requirements.txt
  Install Ollama, run 'ollama serve', pull 'llama3.2'
  Running local Llama server
"""
import os
import json
import requests

from openai import OpenAI
from pydantic import BaseModel, ValidationError

# Ollama client (local LLM)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# # ---------------------------------------------------------------------------
# # Orchestrate Multiple Agents (using local LLM)
# # ---------------------------------------------------------------------------
class TravelOutput(BaseModel):
    destination: str
    duration: str
    summary: str
    cost: str
    tips: str

def web_search(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url)
        data = response.json()
        return data.get('AbstractText', data.get('Answer', 'No information found'))
    except Exception as e:
        return f"Error searching: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information about a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "planner_agent",
            "description": "Call the planner agent to build a day-by-day itinerary",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user prompt"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "budget_agent",
            "description": "Call the budget agent to estimate trip costs",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user prompt"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "local_guide_agent",
            "description": "Call the local guide agent for restaurants and tips",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user prompt"
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]

# ---- Planner Agent (builds day-by-day itinerary) ----
def planner_agent(user_prompt):
    instructions = (
        "You are the Planner Agent. You specialize in building day-by-day travel itineraries and sequencing activities. "
        "Always return your response as valid JSON matching this structure: "
        '{"destination": "string", "duration": "string", "summary": "string"}'
    )
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]
    try:
        response = client.chat.completions.create(
            model="llama3.2",
            messages=messages,
            temperature=0.7,
            tools=tools
        )
        message = response.choices[0].message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.function.name == "web_search":
                    args = json.loads(tool_call.function.arguments)
                    result = web_search(args['query'])
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            response = client.chat.completions.create(
                model="llama3.2",
                messages=messages,
                temperature=0.7,
                tools=tools
            )
        result_content = response.choices[0].message.content
        return result_content
    except Exception as e:
        return f"Error: {e}"

# ---- Budget Agent (estimates costs under constraints) ----
def budget_agent(user_prompt):
    instructions = (
        "You are the Budget Agent. You estimate costs for lodging, food, transport, and activities at a high level; flag budget violations. "
        "Always return your response as valid JSON matching this structure: "
        '{"cost": "string"}'
    )
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]
    try:
        response = client.chat.completions.create(
            model="llama3.2",
            messages=messages,
            temperature=0.7,
            tools=tools
        )
        message = response.choices[0].message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.function.name == "web_search":
                    args = json.loads(tool_call.function.arguments)
                    result = web_search(args['query'])
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            response = client.chat.completions.create(
                model="llama3.2",
                messages=messages,
                temperature=0.7,
                tools=tools
            )
        result_content = response.choices[0].message.content
        return result_content
    except Exception as e:
        return f"Error: {e}"

# ---- Local Guide Agent (adds local tips & dining) ----
def local_guide_agent(user_prompt):
    instructions = (
        "You are the Local Guide Agent. You provide restaurants, neighborhoods, cultural tips, and current local highlights. "
        "Always return your response as valid JSON matching this structure: "
        '{"tips": "string"}'
    )
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]
    try:
        response = client.chat.completions.create(
            model="llama3.2",
            messages=messages,
            temperature=0.7,
            tools=tools
        )
        message = response.choices[0].message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.function.name == "web_search":
                    args = json.loads(tool_call.function.arguments)
                    result = web_search(args['query'])
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            response = client.chat.completions.create(
                model="llama3.2",
                messages=messages,
                temperature=0.7,
                tools=tools
            )
        result_content = response.choices[0].message.content
        return result_content
    except Exception as e:
        return f"Error: {e}"

# ---- Orchestrator (handles calling sub-agents) ----
def orchestrator(user_prompt):
    instructions = (
        "You are the Travel Orchestrator. Your role is to coordinate specialized agents to plan a complete trip.\n"
        "Call the agents in this order: first planner_agent for itinerary, then budget_agent for costs, then local_guide_agent for tips.\n"
        "After getting results from all, combine them into a single JSON response matching this structure:\n"
        '{"destination": "string", "duration": "string", "summary": "string", "cost": "string", "tips": "string"}'
    )
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]
    try:
        print("Orchestrator: Initial LLM call...")
        response = client.chat.completions.create(
            model="llama3.2",
            messages=messages,
            temperature=0.7,
            tools=tools
        )
        message = response.choices[0].message
        tool_call_count = 0
        max_calls = 10  # Prevent infinite loop
        while message.tool_calls and tool_call_count < max_calls:
            tool_call_count += 1
            print(f"Orchestrator: Handling tool calls (iteration {tool_call_count})...")
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"Calling tool: {function_name}")
                if function_name == "web_search":
                    result = web_search(args['query'])
                elif function_name == "planner_agent":
                    result = planner_agent(args['prompt'])
                elif function_name == "budget_agent":
                    result = budget_agent(args['prompt'])
                elif function_name == "local_guide_agent":
                    result = local_guide_agent(args['prompt'])
                else:
                    result = "Unknown tool"
                print(f"Tool result: {result[:100]}...")  # Truncate for brevity
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            print("Orchestrator: Follow-up LLM call...")
            response = client.chat.completions.create(
                model="llama3.2",
                messages=messages,
                temperature=0.7,
                tools=tools
            )
            message = response.choices[0].message
        if tool_call_count >= max_calls:
            print("Orchestrator: Max tool calls reached, stopping.")
        result_content = response.choices[0].message.content
        print(f"Orchestrator: Final result: {result_content}")
        return result_content
    except Exception as e:
        print(f"Orchestrator error: {e}")
        return f"Error: {e}"

# --- Pretty print helper ----------------------------------------------------
def print_fields(data):
    if isinstance(data, str):
        try:
            data = TravelOutput(**json.loads(data))
        except (json.JSONDecodeError, ValidationError) as e:
            print("Raw output:", data)
            return
    print(f"Destination: {data.destination}")
    print(f"Duration: {data.duration}")
    print(f"Summary: {data.summary}")
    print(f"Cost: {data.cost}")
    print(f"Tips: {data.tips}")

def main():
    try:
        prompt = '''I'm considering a trip to New Delhi sometime in late September or early October. 
                                                I'm pretty flexible with the exact dates, maybe around a week-long trip.     
                                                I'd like to get an idea of flight ticket prices and some well-located hotels.     
                                                I'm also a big foodie, so any recommendations for great local restaurants would be fantastic! 
                                                Do not ask follow-up questions.'''
        print("Calling Orchestrator...")
        result = orchestrator(prompt)
        print("Orchestrator result:", result)
        print_fields(result)
    except Exception as e:
        print("Error", e)

if __name__ == "__main__":
    main()