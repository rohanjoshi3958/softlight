# Agent B Architecture

## Overview

Agent B is a generalizable web automation system that:
1. Parses natural language questions into structured workflows
2. Dynamically navigates web applications
3. Captures screenshots of UI states (including non-URL states like modals and forms)

## System Components

### 1. Task Parser (`task_parser.py`)

**Purpose**: Converts natural language questions into structured workflows.

**Key Features**:
- Uses GPT-4 to understand task intent
- Extracts: app name, action, steps, and base URL
- Fallback parser for common patterns

**Input**: "How do I create a project in Linear?"
**Output**: 
```json
{
  "app_name": "Linear",
  "action": "create project",
  "steps": ["Navigate to projects", "Click Create Project", ...],
  "base_url": "https://linear.app"
}
```

### 2. Navigator (`navigator.py`)

**Purpose**: Finds and interacts with UI elements dynamically.

**Element Finding Strategies** (in order of attempt):
1. **Text Content**: Match by visible text
2. **ARIA Labels**: Match by accessibility labels
3. **Role-based**: Find by ARIA role (button, textbox, etc.)
4. **Placeholder**: Match input fields by placeholder text
5. **Semantic**: Use LLM to generate CSS selectors based on page context

**Key Methods**:
- `find_element_by_description()`: Multi-strategy element finding
- `click_element()`: Find and click with state change detection
- `fill_input()`: Find and fill form fields
- `wait_for_modal_or_form()`: Detect when modals/forms appear

### 3. Screenshot Manager (`screenshot_manager.py`)

**Purpose**: Captures and organizes screenshots of UI states.

**Features**:
- Creates task-specific directories
- Timestamps and sequential numbering
- Full-page screenshots
- Descriptive filenames based on state

**Output Structure**:
```
screenshots/
  Linear_create_project_20240101_120000/
    01_initial_page_load.png
    02_after_Navigate_to_projects.png
    03_after_Click_Create_Project.png
    ...
```

### 4. Agent B (`agent_b.py`)

**Purpose**: Main orchestrator that coordinates all components.

**Workflow**:
1. Parse task into workflow
2. Initialize browser and navigate to app
3. For each step:
   - Determine action type (click, fill, wait)
   - Execute action via Navigator
   - Wait for state changes (modals, forms)
   - Capture screenshot
4. Return results with screenshot paths

## Design Decisions

### Why Playwright?
- Modern, fast, and reliable
- Better handling of dynamic content
- Built-in waiting mechanisms
- Cross-browser support

### Why Multiple Element Finding Strategies?
- Web apps use diverse UI patterns
- No single strategy works for all cases
- Fallback chain ensures maximum compatibility

### Why LLM for Task Parsing?
- Natural language understanding
- Generalizable to any app/task
- No hardcoded workflows
- Can adapt to new apps automatically

### Handling Non-URL States

The system captures non-URL states by:
1. **State Detection**: Waiting for modals/forms to appear after interactions
2. **Timing**: Capturing screenshots after each meaningful action
3. **Full-Page Screenshots**: Capturing entire viewport, not just visible area
4. **Sequential Tracking**: Numbering screenshots to show workflow progression

## Limitations & Future Improvements

### Current Limitations:
1. **Authentication**: Requires manual login (could add cookie/session support)
2. **Complex Workflows**: May struggle with multi-step conditional flows
3. **Dynamic Content**: Very dynamic content may need longer wait times
4. **Error Recovery**: Limited retry logic for failed steps

### Potential Improvements:
1. **Session Management**: Save/restore authenticated sessions
2. **Visual Regression**: Compare screenshots to detect state changes
3. **OCR Integration**: Extract text from screenshots for better understanding
4. **Multi-Modal LLM**: Use vision models to understand screenshots
5. **Learning**: Store successful workflows for similar future tasks

## Testing Strategy

The system is tested with:
- **Linear**: Create project, filter issues, change settings
- **Notion**: Create database, filter database

Each test validates:
- Task parsing accuracy
- Element finding success rate
- Screenshot capture completeness
- Workflow execution correctness

