# AI Coding Guidelines for OpenAI Agents SDK Tutorial Repo

## Project Overview
This repository contains progressive Python examples for building AI agents using the OpenAI Agents SDK. Each numbered folder (1-5) represents a lesson, building incrementally from a basic travel agent to advanced features like tools, multi-agent orchestration, guardrails, and sessions.

## Key Architecture Patterns
- **Agent Creation**: Use `Agent` class with `name`, `model` (e.g., "gpt-4"), `instructions` (string with JSON output requirements), `output_type` (Pydantic BaseModel), and `model_settings` (e.g., `ModelSettings(reasoning={"effort": "medium"})`).
- **Output Validation**: Define Pydantic models for structured responses (e.g., `TravelOutput` with `destination`, `duration`, `summary` fields). Instruct agents to return valid JSON matching the model schema.
- **Execution**: Run agents asynchronously with `await Runner.run(agent, prompt)`, accessing results via `result.final_output`.
- **Environment**: Load API keys from `.env` using `load_dotenv(find_dotenv())`; create OpenAI client with `OpenAI(api_key=os.environ['OPENAI_API_KEY'])` (though agents handle API calls internally).

## Common Patterns
- **Incremental Development**: Start with core agent in folder 1, add tools in 2, multi-agent handoffs in 3, guardrails in 4, sessions in 5. Reference `1 Create the Core Travel Agent/agent.py` for base setup.
- **Error Handling**: Wrap `Runner.run` in try/except; use `print_fields` helper to parse and display Pydantic outputs or raw strings on failure.
- **Async Structure**: All agent runs are async; use `asyncio.run(main())` for script entry.
- **Model Settings**: Adjust `reasoning` effort and `extra_body` verbosity based on task complexity (e.g., medium effort for travel planning).

## Developer Workflows
- **Setup**: `pip install -r requirements.txt`, set `OPENAI_API_KEY` in `.env`, run `python agent.py` in each folder.
- **Testing**: Execute scripts directly; outputs are printed to console. No formal tests—validate by running and checking JSON structure.
- **Extensions**: Add tools as functions with `@tool` decorator (see folder 2), use `handoffs` for agent delegation (folder 3), implement `guardrails` for safety (folder 4), enable `sessions` for context (folder 5).

## Conventions
- Folder structure: Numbered lessons with `agent.py` each; root has shared `requirements.txt` and `README.md`.
- Imports: Standard libraries first, then `openai`, `agents`, `pydantic`, `dotenv`.
- Comments: Use `# --- Section ---` for code blocks; docstrings at top with prereqs.
- Avoid hardcoding: Use env vars for keys; no API calls outside agents.

Reference `README.md` for course overview and `INSTRUCTOR_INSTRUCTIONS/` for setup details.