# Quick Start Guide - Get Running in 5 Minutes

This guide will get you up and running with the OpenAI Agents SDK travel planner in the fastest way possible.

---

## Prerequisites ✅

Before starting, ensure you have:
- **Python 3.9+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** installed ([Download Git](https://git-scm.com/downloads))
- **OpenAI API Key** ([Get API Key](https://platform.openai.com/api-keys))
- **Code Editor** (VS Code recommended)

---

## 5-Minute Setup 🚀

### Step 1: Clone Repository (30 seconds)

```bash
# Clone the repository
git clone <repository-url>
cd build-with-ai-create-agents-with-the-openai-agents-sdk-ugc-4740011
```

### Step 2: Create Virtual Environment (30 seconds)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed openai-2.6.1 python-dotenv openai-agents fastapi pydantic requests
```

### Step 4: Configure API Key (1 minute)

Create a `.env` file in the project root:

```bash
# Windows PowerShell
echo OPENAI_API_KEY=sk-your-key-here > .env

# macOS/Linux
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

Or manually create `.env`:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

⚠️ **Never commit `.env` to git!** It's already in `.gitignore`.

### Step 5: Run Your First Agent (2 minutes)

```bash
# Navigate to lesson 1
cd "1 Create the Core Travel Agent"

# Run the agent
python agent.py
```

**Expected Output:**
```
Starting agent...
Calling Ollama API...
API call successful.
Raw response: {"destination":"Mussoorie","duration":"3 days"...}
Destination: Mussoorie
Duration: 3 days
Summary: A 3-day budget trip exploring hidden gems...
```

✅ **Success!** Your first agent is running.

---

## Testing All Lessons (Optional)

### Lesson 1: Core Agent
```bash
cd "1 Create the Core Travel Agent"
python agent.py
```
**What it does**: Basic travel agent with structured JSON output

### Lesson 2: Tools
```bash
cd "2 Extend the Agent with Tools"
python agent.py
```
**What it does**: Adds web search capability

### Lesson 3: Multi-Agent
```bash
cd "3 Orchestrate Mulitple Agents"
python agent.py
```
**What it does**: Orchestrates planner, budget, and guide agents

### Lesson 4: Guardrails
```bash
cd "4 Add Agent Guardrails for Safe Responses"
python agent.py
```
**What it does**: Validates budget constraints before planning

### Lesson 5: Sessions
```bash
cd "5 Maintain Agent Context with Sessions"
python agent.py
```
**What it does**: Remembers conversation context across multiple turns

---

## Common Quick Start Issues 🔧

### Issue 1: `ModuleNotFoundError: No module named 'openai'`
**Solution**: Activate virtual environment
```bash
# Windows
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### Issue 2: `openai.AuthenticationError: Invalid API key`
**Solution**: Check your `.env` file
```bash
# Verify file exists
cat .env  # macOS/Linux
type .env # Windows

# Should contain:
# OPENAI_API_KEY=sk-proj-...
```

### Issue 3: `ImportError: cannot import name 'Agent' from 'agents'`
**Solution**: Update package
```bash
pip install --upgrade openai-agents
```

### Issue 4: Python version too old
**Solution**: Verify Python version
```bash
python --version  # Should be 3.9 or higher
```

---

## Alternative: Using Ollama (Local LLM) 🏠

If you don't have an OpenAI API key, you can use Ollama for local testing:

### 1. Install Ollama
- **Windows**: Download from [ollama.com](https://ollama.com)
- **macOS**: `brew install ollama`
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

### 2. Start Ollama Server
```bash
ollama serve
```

### 3. Pull Model
```bash
ollama pull llama3.2
```

### 4. Run Lesson 1-3 (Already Configured for Ollama)
```bash
cd "1 Create the Core Travel Agent"
python agent.py
```

**Note**: Lessons 4-5 require OpenAI API as they use `gpt-5` model.

---

## Quick Verification Checklist ✔️

- [ ] Virtual environment activated (you see `(venv)` in terminal)
- [ ] Dependencies installed (`pip list | grep openai`)
- [ ] `.env` file created with valid API key
- [ ] Lesson 1 runs successfully
- [ ] You see JSON output with destination, duration, summary

---

## Next Steps After Quick Start

### Beginner Path
1. **Read code**: Open `1 Create the Core Travel Agent/agent.py` in VS Code
2. **Modify prompt**: Change travel destination in `main()` function
3. **Run again**: See how output changes
4. **Progress**: Move to Lesson 2

### Advanced Path
1. **Read**: [03_ARCHITECTURE.md](./03_ARCHITECTURE.md) - System design
2. **Study**: [06_LESSON_BY_LESSON_GUIDE.md](./06_LESSON_BY_LESSON_GUIDE.md) - Code deep dive
3. **Build**: Create your own custom agent

### Production Path
1. **Read**: [12_PRODUCTIONIZATION_GUIDE.md](./12_PRODUCTIONIZATION_GUIDE.md)
2. **Implement**: Error handling, logging, monitoring
3. **Deploy**: Containerize and deploy to cloud

---

## Quick Command Reference

### Environment Management
```bash
# Activate venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# Deactivate venv
deactivate

# Install new package
pip install package-name

# Update requirements
pip freeze > requirements.txt
```

### Running Agents
```bash
# Run specific lesson
cd "X Lesson Name"
python agent.py

# Run with verbose output
python -u agent.py

# Run with Python debugger
python -m pdb agent.py
```

### Testing
```bash
# Check syntax
python -m py_compile agent.py

# Check imports
python -c "from agents import Agent; print('Success')"

# Test OpenAI connection
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print(client.models.list())"
```

---

## File Structure After Quick Start

```
build-with-ai-create-agents-with-the-openai-agents-sdk-ugc-4740011/
├── .env                                          ✅ (You created this)
├── venv/                                         ✅ (Virtual environment)
├── requirements.txt                              ✅ (Dependencies)
├── 1 Create the Core Travel Agent/
│   └── agent.py                                 ✅ (Run this first)
├── 2 Extend the Agent with Tools/
│   └── agent.py                                 ✅ (Second lesson)
├── ... (other lessons)
└── DEVELOPER_DOCUMENTATION/                      ✅ (You're here!)
```

---

## Performance Expectations

### First Run
- **Time**: 5-15 seconds (depends on model & network)
- **Cost**: ~$0.01-0.05 (OpenAI API)
- **Output**: JSON with destination, duration, summary

### Subsequent Runs
- **Time**: 2-10 seconds (cached models)
- **Cost**: Same per request
- **Output**: Varies based on prompt

---

## Getting Help 🆘

### If Things Don't Work
1. **Check**: [13_TROUBLESHOOTING.md](./13_TROUBLESHOOTING.md)
2. **Debug**: Enable verbose logging (see below)
3. **Verify**: API key is valid and has credits

### Enable Debug Logging
Add this to top of `agent.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check OpenAI API Status
```bash
# Test API key validity
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv, find_dotenv; load_dotenv(find_dotenv()); client = OpenAI(api_key=os.environ['OPENAI_API_KEY']); print('API Key Valid:', bool(client.models.list()))"
```

---

## What You Just Accomplished 🎉

✅ Installed OpenAI Agents SDK  
✅ Configured development environment  
✅ Ran your first AI agent  
✅ Saw structured output from LLM  
✅ Ready to dive deeper into agent patterns

**Time Invested**: ~5 minutes  
**Knowledge Gained**: Core agent setup & execution  
**Next Milestone**: Understand agent architecture ([03_ARCHITECTURE.md](./03_ARCHITECTURE.md))

---

**Pro Tip**: Keep your terminal open with venv activated as you work through lessons. This avoids repeated activation steps.

---

**Document Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**Target Audience**: New developers setting up for first time
