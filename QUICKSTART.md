# Quick Start Guide

## Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection

## Setup (5 minutes)

1. **Clone/Navigate to the project**:
```bash
cd softlight
```

2. **Run setup script**:
```bash
./setup.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

3. **Configure API key**:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Running Your First Task

### Example 1: Create a Project in Linear

```bash
python main.py "How do I create a project in Linear?" --url https://linear.app
```

**Note**: You may need to log in to Linear first. The browser will open, and you can log in manually. The agent will then proceed with the task.

### Example 2: Filter a Database in Notion

```bash
python main.py "How do I filter a database in Notion?" --url https://www.notion.so
```

### Example 3: Using Python API

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
        print(f"Success: {result['success']}")
        print(f"Screenshots: {len(result['screenshots'])}")
    finally:
        await agent.close()

asyncio.run(main())
```

## Running Example Tests

Test all Linear workflows:
```bash
python examples/test_linear.py
```

Test all Notion workflows:
```bash
python examples/test_notion.py
```

Run all tests:
```bash
python examples/run_all.py
```

## Viewing Results

Screenshots are saved in the `screenshots/` directory:
```
screenshots/
  Linear_create_project_20240101_120000/
    01_initial_page_load.png
    02_after_Navigate_to_projects.png
    03_after_Click_Create_Project.png
    ...
```

## Troubleshooting

### "Could not find element" errors
- The UI might have changed
- Try rephrasing your question
- Check if you're logged in to the app

### Browser doesn't open
- Make sure Playwright browsers are installed: `playwright install chromium`
- Check if you're running in headless mode (remove `--headless` flag)

### API errors
- Verify your OpenAI API key is set in `.env`
- Check your API quota/limits

### Authentication required
- Many apps require login
- The browser will open - log in manually
- The agent will wait and then proceed

## Tips

1. **Be specific**: "How do I create a project in Linear?" is better than "create project"
2. **Include app name**: Always mention the app in your question
3. **Watch the browser**: Keep it visible to see what's happening
4. **Check screenshots**: Review captured screenshots to verify the workflow

