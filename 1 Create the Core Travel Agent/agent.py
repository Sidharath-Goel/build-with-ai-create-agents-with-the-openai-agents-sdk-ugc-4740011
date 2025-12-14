"""
Build with AI: Create Agents with the OpenAI Agents SDK
All examples use Python and the OpenAI client.

Prereqs:
  pip install -r requirements.txt
  Install Ollama, run 'ollama serve', pull 'llama3.2'
..Running local Llama server
  """


import asyncio
import json

from openai import OpenAI
from pydantic import BaseModel, ValidationError

# Ollama client (local LLM)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# # ---------------------------------------------------------------------------
# # Create the Core Travel Agent (using Ollama directly)
# # ---------------------------------------------------------------------------
class TravelOutput(BaseModel):
    destination: str
    duration: str
    summary: str

instructions = (
    "You are a friendly and knowledgeable travel planner that helps users plan trips, "
    "suggest destinations, and create brief summaries of their journeys. "
    "Always return your response as valid JSON matching this structure: "
    '{"destination": "string", "duration": "string", "summary": "string"}'
)

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

def main():
    print("Starting agent...")
    try:
        print("Calling Ollama API...")
        response = client.chat.completions.create(
            model="llama3.2",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": "Plan a 3-day trip to Mussorie under INR 5000. Find uncommon places that are off the beaten path and little known."}
            ],
            temperature=0.7
        )
        print("API call successful.")
        result_content = response.choices[0].message.content
        print(f"Raw response: {result_content}")
        print_fields(result_content)
    except Exception as e:
        print("Error", e)

if __name__ == "__main__":
    main()