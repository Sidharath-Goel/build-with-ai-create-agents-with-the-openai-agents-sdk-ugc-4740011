# Environment Setup - Detailed Configuration Guide

This document provides comprehensive environment setup instructions for the OpenAI Agents SDK project, covering multiple operating systems, configurations, and development scenarios.

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Python Installation](#python-installation)
3. [Virtual Environment Setup](#virtual-environment-setup)
4. [Dependency Installation](#dependency-installation)
5. [API Key Configuration](#api-key-configuration)
6. [IDE Configuration](#ide-configuration)
7. [Alternative Setups](#alternative-setups)
8. [Verification & Testing](#verification--testing)

---

## System Requirements

### Minimum Requirements
| Component | Specification |
|-----------|---------------|
| **OS** | Windows 10+, macOS 10.15+, Ubuntu 20.04+ |
| **Python** | 3.9 or higher |
| **RAM** | 4GB minimum, 8GB recommended |
| **Disk Space** | 500MB for dependencies + virtual environment |
| **Network** | Stable internet connection for API calls |

### Recommended Requirements
| Component | Specification |
|-----------|---------------|
| **Python** | 3.11 or 3.12 (best performance) |
| **RAM** | 16GB for comfortable development |
| **CPU** | Multi-core processor for async operations |
| **Editor** | VS Code with Python extension |

---

## Python Installation

### Windows

#### Option 1: Official Installer (Recommended)
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer with **"Add Python to PATH"** checked
3. Verify installation:
```powershell
python --version
# Output: Python 3.11.x
```

#### Option 2: Microsoft Store
```powershell
# Search "Python 3.11" in Microsoft Store
# Install directly from store
```

#### Option 3: Chocolatey Package Manager
```powershell
choco install python --version=3.11.5
```

### macOS

#### Option 1: Official Installer
1. Download from [python.org](https://www.python.org/downloads/)
2. Install .pkg file
3. Verify:
```bash
python3 --version
```

#### Option 2: Homebrew (Recommended)
```bash
brew install python@3.11
```

#### Option 3: pyenv (Version Management)
```bash
brew install pyenv
pyenv install 3.11.5
pyenv global 3.11.5
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Verify
python3.11 --version
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3.11 python3.11-pip
```

---

## Virtual Environment Setup

Virtual environments isolate project dependencies from system Python.

### Why Virtual Environments?
- ✅ Isolate project dependencies
- ✅ Avoid version conflicts
- ✅ Easy cleanup (just delete folder)
- ✅ Reproducible environments

### Windows Setup

#### PowerShell (Recommended)
```powershell
# Navigate to project root
cd path\to\build-with-ai-create-agents-with-the-openai-agents-sdk-ugc-4740011

# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then retry activation
```

#### Command Prompt
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### macOS/Linux Setup

```bash
# Navigate to project root
cd /path/to/build-with-ai-create-agents-with-the-openai-agents-sdk-ugc-4740011

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify activation (should see (venv) prefix)
which python
# Output: /path/to/project/venv/bin/python
```

### Verify Virtual Environment

After activation, you should see:
```
(venv) PS C:\...\build-with-ai-create-agents-with-the-openai-agents-sdk-ugc-4740011>
```

---

## Dependency Installation

### Install from requirements.txt

```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

### Expected Installation Output
```
Collecting openai==2.6.1
  Downloading openai-2.6.1-py3-none-any.whl (...)
Collecting python-dotenv
  Downloading python_dotenv-1.0.0-py3-none-any.whl (...)
Collecting openai-agents
  Downloading openai_agents-0.1.0-py3-none-any.whl (...)
...
Successfully installed openai-2.6.1 python-dotenv-1.0.0 openai-agents-0.1.0 ...
```

### Individual Package Installation

If you need to install packages one by one:

```bash
pip install openai==2.6.1
pip install python-dotenv
pip install openai-agents
pip install fastapi
pip install pydantic
pip install requests
```

### Upgrade Packages (If Needed)

```bash
# Upgrade all packages
pip install --upgrade -r requirements.txt

# Upgrade specific package
pip install --upgrade openai-agents
```

### Verify Installation

```bash
# List installed packages
pip list

# Check specific package
pip show openai-agents

# Verify imports
python -c "from agents import Agent; print('Success')"
python -c "from openai import OpenAI; print('Success')"
python -c "from pydantic import BaseModel; print('Success')"
```

---

## API Key Configuration

### OpenAI API Key

#### 1. Obtain API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy key (starts with `sk-proj-...` or `sk-...`)

⚠️ **Important**: Store securely, never commit to git!

#### 2. Create .env File

**Project root location**:
```
build-with-ai-create-agents-with-the-openai-agents-sdk-ugc-4740011/.env
```

**Windows (PowerShell)**:
```powershell
# Create file
New-Item -Path .env -ItemType File

# Add content
Set-Content -Path .env -Value "OPENAI_API_KEY=sk-proj-your-actual-key-here"
```

**macOS/Linux**:
```bash
# Create and populate in one command
cat > .env << EOF
OPENAI_API_KEY=sk-proj-your-actual-key-here
EOF
```

**Manual Creation**:
1. Open text editor
2. Create file named `.env` (with leading dot)
3. Add content:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxx
```
4. Save in project root

#### 3. Verify .env File

```bash
# Windows
type .env

# macOS/Linux
cat .env

# Should output:
# OPENAI_API_KEY=sk-proj-...
```

#### 4. Test API Key

```python
# Create test file: test_api_key.py
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("✅ API Key Valid!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print("❌ API Key Invalid or Error:", e)
```

```bash
python test_api_key.py
```

### Environment Variables (Alternative Methods)

#### System Environment Variables (Persistent)

**Windows**:
```powershell
# Set permanently
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-...', 'User')

# Verify
$env:OPENAI_API_KEY
```

**macOS/Linux**:
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $OPENAI_API_KEY
```

#### Session Environment Variables (Temporary)

**Windows PowerShell**:
```powershell
$env:OPENAI_API_KEY = "sk-proj-..."
```

**macOS/Linux**:
```bash
export OPENAI_API_KEY="sk-proj-..."
```

⚠️ **Note**: Session variables are lost when terminal closes.

---

## IDE Configuration

### Visual Studio Code (Recommended)

#### 1. Install VS Code
Download from [code.visualstudio.com](https://code.visualstudio.com/)

#### 2. Install Python Extension
1. Open VS Code
2. Click Extensions icon (Ctrl+Shift+X)
3. Search "Python" (by Microsoft)
4. Click Install

#### 3. Configure Python Interpreter
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose `./venv/bin/python` (or `.\venv\Scripts\python.exe` on Windows)

#### 4. Install Recommended Extensions
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "tamasfe.even-better-toml"
  ]
}
```

#### 5. Configure Workspace Settings
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

#### 6. Create Launch Configuration
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: Lesson 1",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/1 Create the Core Travel Agent/agent.py",
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

### PyCharm

#### 1. Configure Interpreter
1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `./venv/bin/python`

#### 2. Configure .env File Support
1. Install "EnvFile" plugin
2. Run → Edit Configurations
3. Enable "EnvFile" tab
4. Add `.env` file path

### Jupyter Notebook (Optional)

```bash
pip install jupyter
jupyter notebook

# Or use VS Code Jupyter extension
```

---

## Alternative Setups

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=""

CMD ["python", "1 Create the Core Travel Agent/agent.py"]
```

Build and run:
```bash
docker build -t openai-agents .
docker run -e OPENAI_API_KEY=sk-proj-... openai-agents
```

### Using Poetry (Advanced Dependency Management)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Initialize project
poetry init

# Add dependencies
poetry add openai==2.6.1 python-dotenv openai-agents fastapi pydantic requests

# Activate environment
poetry shell

# Run
python agent.py
```

### Using Conda

```bash
# Create environment
conda create -n openai-agents python=3.11

# Activate
conda activate openai-agents

# Install dependencies
pip install -r requirements.txt
```

### Using Ollama (Local LLM - No API Key)

#### 1. Install Ollama
- **Windows**: Download installer from [ollama.com](https://ollama.com/download)
- **macOS**: `brew install ollama`
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

#### 2. Start Server
```bash
ollama serve
```

#### 3. Pull Model
```bash
ollama pull llama3.2
```

#### 4. Configure (Already Done in Lessons 1-3)
```python
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Dummy key for local
)
```

⚠️ **Note**: Lessons 4-5 require OpenAI API (use GPT-5 model).

---

## Verification & Testing

### Complete Verification Script

Create `verify_setup.py`:
```python
#!/usr/bin/env python3
"""
Comprehensive setup verification script
"""
import sys
import os

def check_python_version():
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True
    else:
        print(f"❌ Python version {sys.version.split()[0]} is too old. Need 3.9+")
        return False

def check_dependencies():
    required = {
        'openai': '2.6.1',
        'dotenv': 'python-dotenv',
        'agents': 'openai-agents',
        'pydantic': 'pydantic',
        'requests': 'requests'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            if module == 'dotenv':
                import dotenv
                print(f"✅ {package}: {dotenv.__version__}")
            elif module == 'agents':
                import agents
                print(f"✅ {package}: installed")
            else:
                mod = __import__(module)
                print(f"✅ {package}: {mod.__version__}")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_env_file():
    if os.path.exists('.env'):
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content:
                print("✅ OPENAI_API_KEY found in .env")
                return True
            else:
                print("❌ OPENAI_API_KEY not found in .env")
                return False
    else:
        print("❌ .env file missing")
        return False

def check_api_key():
    from openai import OpenAI
    from dotenv import load_dotenv, find_dotenv
    
    load_dotenv(find_dotenv())
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not loaded")
        return False
    
    if api_key.startswith('sk-'):
        print("✅ OPENAI_API_KEY format valid")
        
        # Test API call
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            print("✅ OpenAI API connection successful")
            return True
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return False
    else:
        print("❌ OPENAI_API_KEY format invalid")
        return False

def main():
    print("=" * 50)
    print("OpenAI Agents SDK Setup Verification")
    print("=" * 50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("API Key", check_api_key)
    ]
    
    results = []
    for name, check in checks:
        print(f"\n--- {name} ---")
        results.append(check())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ ALL CHECKS PASSED - Setup Complete!")
    else:
        print("❌ SOME CHECKS FAILED - Review errors above")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

Run verification:
```bash
python verify_setup.py
```

### Quick Verification Commands

```bash
# 1. Python version
python --version

# 2. Virtual environment active
which python  # macOS/Linux
where python  # Windows

# 3. Packages installed
pip list | grep openai

# 4. Env file exists
ls -la .env  # macOS/Linux
dir .env     # Windows

# 5. Import test
python -c "from agents import Agent; from openai import OpenAI; from pydantic import BaseModel; print('All imports OK')"
```

---

## Troubleshooting

### Common Issues

#### Issue: `pip: command not found`
**Solution**:
```bash
python -m ensurepip --upgrade
python -m pip --version
```

#### Issue: Virtual environment not activating (Windows)
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: `ModuleNotFoundError` after installation
**Solution**: Ensure virtual environment is activated
```bash
# Deactivate and reactivate
deactivate
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux
```

#### Issue: Multiple Python versions conflict
**Solution**: Use explicit version commands
```bash
python3.11 -m venv venv
./venv/bin/python --version
```

---

## Best Practices

### ✅ DO
- Always use virtual environments
- Keep `.env` file out of version control
- Update dependencies regularly (but test first)
- Document environment-specific configurations
- Use `requirements.txt` for reproducibility

### ❌ DON'T
- Install packages globally (outside venv)
- Commit API keys to git
- Mix conda and venv environments
- Ignore security updates
- Use outdated Python versions

---

## Next Steps

After successful environment setup:

1. **Test**: Run [01_QUICK_START.md](./01_QUICK_START.md) verification
2. **Learn**: Read [03_ARCHITECTURE.md](./03_ARCHITECTURE.md)
3. **Code**: Start with Lesson 1: [06_LESSON_BY_LESSON_GUIDE.md](./06_LESSON_BY_LESSON_GUIDE.md)
4. **Extend**: Plan production modifications

---

**Document Version**: 1.0.0  
**Last Updated**: December 29, 2025  
**Target Audience**: DevOps, Backend Engineers, New Team Members
