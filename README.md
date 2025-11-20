# Agent B: Web Automation & Screenshot Capture System

Agent B is an AI-powered system that automatically navigates web applications and captures screenshots of UI states to demonstrate how to perform tasks.

## Features

- **Natural Language Task Understanding**: Parses questions like "How do I create a project in Linear?" and determines the workflow
- **Dynamic Navigation**: Automatically finds and interacts with UI elements without hardcoded selectors
- **State-Aware Screenshot Capture**: Captures screenshots at each meaningful UI state, including modals, forms, and other non-URL states
- **Generalizable**: Works across different web apps without task-specific code

## Installation

### Quick Setup

Run the setup script:
```bash
./setup.sh
```

Or manually:

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Set up environment variables:
```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

## Usage

### Command Line

```bash
python main.py "How do I create a project in Linear?" --url https://linear.app
```

Options:
- `--url`: Override the base URL (optional)
- `--headless`: Run browser in headless mode
- `--slow-mo`: Slow down operations by milliseconds (default: 500)

### Python API

```python
import asyncio
from agent_b import AgentB

async def main():
    agent = AgentB(headless=False, slow_mo=500)
    try:
        result = await agent.execute_task(
            "How do I create a project in Linear?",
            base_url="https://linear.app"
        )
        print(f"Captured {len(result['screenshots'])} screenshots")
    finally:
        await agent.close()

asyncio.run(main())
```

## Example Workflows

See the `examples/` directory for test scripts demonstrating:
- Creating a project in Linear
- Filtering issues in Linear
- Creating a database in Notion
- Filtering a database in Notion

## How It Works

1. **Task Parsing**: Uses LLM to understand the task and extract:
   - Target application
   - Action to perform
   - Key steps in the workflow

2. **Navigation**: 
   - Finds UI elements by text, role, and semantic meaning
   - Interacts with buttons, forms, and other controls
   - Waits for state changes (modals, forms, etc.)

3. **Screenshot Capture**:
   - Captures screenshots at each meaningful state
   - Tracks state transitions (page loads, modal opens, form submissions)
   - Saves screenshots with descriptive names

## Output

Screenshots are saved in the `screenshots/` directory, organized by task and timestamp.

## Authentication Note

Many web applications require authentication. When running Agent B:
1. The browser will open (unless `--headless` is used)
2. You may need to manually log in to the application
3. After logging in, Agent B will proceed with the task
4. Future improvements could include session management for automatic authentication

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step guide to get started.


