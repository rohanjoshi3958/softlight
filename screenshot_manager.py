"""
Screenshot Manager: Handles capturing and organizing screenshots of UI states.
"""
import os
from datetime import datetime
from typing import Optional
from playwright.async_api import Page
from pathlib import Path


class ScreenshotManager:
    """Manages screenshot capture and organization."""
    
    def __init__(self, output_dir: str = "screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_task_dir: Optional[Path] = None
        self.screenshot_count = 0
    
    def start_task(self, task_name: str):
        """Initialize a new task directory for screenshots."""
        # Create a sanitized task name for directory
        safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')[:50]  # Limit length
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_dir_name = f"{safe_name}_{timestamp}"
        
        self.current_task_dir = self.output_dir / task_dir_name
        self.current_task_dir.mkdir(exist_ok=True)
        self.screenshot_count = 0
        
        print(f"Screenshots will be saved to: {self.current_task_dir}")
    
    async def capture_state(self, page: Page, state_description: str) -> Optional[str]:
        """
        Capture a screenshot of the current UI state.
        
        Args:
            page: Playwright page object
            state_description: Description of the current state
            
        Returns:
            Path to saved screenshot or None if failed
        """
        if not self.current_task_dir:
            self.start_task("default_task")
        
        self.screenshot_count += 1
        
        # Create safe filename from description
        safe_desc = "".join(c for c in state_description if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_desc = safe_desc.replace(' ', '_')[:40]
        
        filename = f"{self.screenshot_count:02d}_{safe_desc}.png"
        filepath = self.current_task_dir / filename
        
        try:
            await page.screenshot(path=str(filepath), full_page=True)
            print(f"Captured screenshot: {filename} - {state_description}")
            return str(filepath)
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None
    
    async def capture_current_page(self, page: Page, description: str = "current_state") -> Optional[str]:
        """Capture screenshot of current page with description."""
        return await self.capture_state(page, description)
    
    def get_task_directory(self) -> Optional[str]:
        """Get the current task directory path."""
        return str(self.current_task_dir) if self.current_task_dir else None

