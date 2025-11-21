"""
Task Parser: Converts natural language questions into actionable workflows.
"""
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class TaskParser:
    """Parses natural language tasks into structured workflows."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def parse_task(self, question: str) -> Dict:
        """
        Parse a natural language question into a structured workflow.
        
        Args:
            question: Natural language question like "How do I create a project in Linear?"
            
        Returns:
            Dictionary with:
            - app_name: Name of the application
            - action: Main action to perform
            - steps: List of steps to execute
            - base_url: Base URL of the application
        """
        prompt = f"""Parse this question into a structured workflow: "{question}"

Extract:
1. The application name (e.g., Linear, Notion, Asana)
2. The main action (e.g., "create project", "filter database", "change settings")
3. A list of 3-7 specific steps needed to complete the task
4. The base URL for the application

Return a JSON object with this structure:
{{
    "app_name": "application name",
    "action": "main action description",
    "steps": [
        "step 1 description",
        "step 2 description",
        ...
    ],
    "base_url": "https://app-url.com"
}}

For each step, describe what UI element to find or what action to take.
Be specific about button labels, menu items, or form fields to look for.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that parses user questions into structured workflows. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            workflow = json.loads(content)
            return workflow
            
        except Exception as e:
            print(f"Error parsing task: {e}")
            # Fallback parsing
            return self._fallback_parse(question)
    
    def _fallback_parse(self, question: str) -> Dict:
        """Simple fallback parser for common patterns."""
        question_lower = question.lower()
        
        # Extract app name
        apps = ["linear", "notion", "asana", "trello", "jira"]
        app_name = "Unknown"
        for app in apps:
            if app in question_lower:
                app_name = app.capitalize()
                break
        
        # Extract action
        action = "perform task"
        if "create" in question_lower and "project" in question_lower:
            action = "create project"
        elif "filter" in question_lower:
            action = "filter"
        elif "change" in question_lower or "update" in question_lower:
            action = "update settings"
        
        # Base URLs
        base_urls = {
            "Linear": "https://linear.app",
            "Notion": "https://www.notion.so",
            "Asana": "https://app.asana.com",
        }
        
        return {
            "app_name": app_name,
            "action": action,
            "steps": [
                "Navigate to the application",
                f"Find and click the button or menu item to {action}",
                "Fill in any required forms",
                "Complete the action"
            ],
            "base_url": base_urls.get(app_name, "https://example.com")
        }


