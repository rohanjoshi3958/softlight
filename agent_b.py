"""
Agent B: Main agent that orchestrates task execution, navigation, and screenshot capture.
"""
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from task_parser import TaskParser
from navigator import Navigator
from screenshot_manager import ScreenshotManager


class AgentB:
    """
    Agent B: Executes tasks by navigating web applications and capturing UI states.
    """
    
    def __init__(self, headless: bool = False, slow_mo: int = 500):
        """
        Initialize Agent B.
        
        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by milliseconds (for visibility)
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.task_parser = TaskParser()
        self.screenshot_manager = ScreenshotManager()
        self.navigator: Optional[Navigator] = None
    
    async def _initialize_browser(self):
        """Initialize Playwright browser."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            # Try multiple launch strategies for macOS compatibility
            # Note: Firefox uses different args than Chromium
            launch_strategies = [
                # Strategy 1: Minimal args (most compatible)
                {
                    "headless": self.headless,
                    "slow_mo": self.slow_mo,
                },
                # Strategy 2: Force headless if non-headless failed
                {
                    "headless": True,
                    "slow_mo": self.slow_mo,
                } if not self.headless else None,
            ]
            
            last_error = None
            for i, launch_args in enumerate(launch_strategies):
                if launch_args is None:
                    continue
                    
                try:
                    print(f"Attempting Firefox launch (strategy {i+1})...")
                    self.browser = await self.playwright.firefox.launch(**launch_args)
                    
                    # Wait a moment to ensure browser stays alive
                    await asyncio.sleep(0.5)
                    
                    # Verify browser is actually running by checking if we can create a context
                    test_context = await self.browser.new_context()
                    await test_context.close()
                    
                    print("Browser launched successfully!")
                    break
                except Exception as e:
                    last_error = e
                    if self.browser:
                        try:
                            await self.browser.close()
                        except:
                            pass
                        self.browser = None
                    continue
            
            if not self.browser:
                error_msg = str(last_error) if last_error else "Unknown error"
                print(f"\n❌ Error launching browser: {error_msg}")
                print("\n🔧 Troubleshooting steps:")
                print("1. Install Firefox browser:")
                print("   playwright install firefox")
                print("2. Reinstall if needed:")
                print("   playwright install firefox --force")
                print("3. Check macOS permissions:")
                print("   System Settings > Privacy & Security > Accessibility")
                print("   Allow Terminal/iTerm to control your computer")
                print("4. Try running in headless mode:")
                print("   python main.py 'your question' --headless")
                print("5. Update Playwright:")
                print("   pip install --upgrade playwright")
                raise RuntimeError(f"Browser launch failed after all strategies: {error_msg}") from last_error
        
        if not self.context:
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
        
        if not self.page:
            self.page = await self.context.new_page()
            self.navigator = Navigator(self.page)
    
    async def execute_task(self, question: str, base_url: Optional[str] = None) -> dict:
        """
        Execute a task based on a natural language question.
        
        Args:
            question: Natural language question (e.g., "How do I create a project in Linear?")
            base_url: Optional base URL to override parsed URL
            
        Returns:
            Dictionary with execution results
        """
        await self._initialize_browser()
        
        print(f"\n{'='*60}")
        print(f"Executing task: {question}")
        print(f"{'='*60}\n")
        
        # Parse the task
        print("Parsing task...")
        workflow = self.task_parser.parse_task(question)
        print(f"App: {workflow['app_name']}")
        print(f"Action: {workflow['action']}")
        print(f"Steps: {len(workflow['steps'])} steps identified\n")
        
        # Override base URL if provided
        if base_url:
            workflow['base_url'] = base_url
        
        # Initialize screenshot manager for this task
        task_name = f"{workflow['app_name']}_{workflow['action']}"
        self.screenshot_manager.start_task(task_name)
        
        results = {
            "question": question,
            "workflow": workflow,
            "screenshots": [],
            "success": False,
            "errors": []
        }
        
        try:
            # Step 1: Navigate to the application
            print(f"Step 1: Navigating to {workflow['base_url']}...")
            await self.page.goto(workflow['base_url'], wait_until="networkidle")
            await asyncio.sleep(2)  # Wait for page to fully load
            
            screenshot_path = await self.screenshot_manager.capture_current_page(
                self.page, "initial_page_load"
            )
            if screenshot_path:
                results["screenshots"].append(screenshot_path)
            
            # Step 1.5: Check for login and wait if needed
            # Only auto-detect login if there's no explicit login step in the workflow
            has_login_step = any(
                any(word in step.lower() for word in ["log in", "login", "sign in", "signin", "authenticate"])
                for step in workflow['steps']
            )
            
            if not has_login_step:
                # No explicit login step, so check if we need to log in automatically
                print("\nChecking authentication status...")
                if await self.navigator.is_login_page():
                    print("Login page detected (no login step in workflow).")
                    login_completed = await self.navigator.wait_for_login(timeout=300000)  # 5 minutes
                    
                    if login_completed:
                        print("\n✓ Authentication successful! Proceeding with task...\n")
                        # Capture screenshot after login
                        await asyncio.sleep(2)  # Wait for page to settle
                        screenshot_path = await self.screenshot_manager.capture_current_page(
                            self.page, "after_login"
                        )
                        if screenshot_path:
                            results["screenshots"].append(screenshot_path)
                    else:
                        print("\n⚠ Proceeding anyway - please ensure you're logged in.\n")
                else:
                    print("✓ Already authenticated or no login required.\n")
            else:
                print("✓ Login step found in workflow - will handle during step execution.\n")
            
            # Execute each step in the workflow
            for i, step in enumerate(workflow['steps'], start=2):
                print(f"\nStep {i}: {step}")
                
                try:
                    # Determine action type from step description
                    step_lower = step.lower()
                    
                    # Special handling for login steps
                    if any(word in step_lower for word in ["log in", "login", "sign in", "signin", "authenticate"]):
                        print("  🔐 Login step detected - waiting for manual login...")
                        
                        # Check if we're already on a login page
                        is_on_login_page = await self.navigator.is_login_page()
                        
                        if not is_on_login_page:
                            # Not on login page yet - try to navigate to it
                            print("  Navigating to login page...")
                            
                            # Capture screenshot before navigating to login
                            screenshot_path = await self.screenshot_manager.capture_current_page(
                                self.page, f"before_login_step_{i}"
                            )
                            if screenshot_path:
                                results["screenshots"].append(screenshot_path)
                            
                            # Try to find and click a login button/link (but don't be verbose about it)
                            # Only try common login button texts, not the whole step description
                            login_button_texts = ["log in", "login", "sign in", "signin", "sign in"]
                            login_found = False
                            
                            for button_text in login_button_texts:
                                try:
                                    # Use a quiet method to find login button
                                    element = await self.page.get_by_text(button_text, exact=False).first.wait_for(
                                        state="visible", timeout=3000
                                    )
                                    if element:
                                        await element.click()
                                        login_found = True
                                        print(f"  ✓ Clicked '{button_text}' button")
                                        break
                                except:
                                    continue
                            
                            if login_found:
                                await asyncio.sleep(2)  # Wait for login page to load
                                # Verify we're now on login page
                                is_on_login_page = await self.navigator.is_login_page()
                            
                            if is_on_login_page:
                                # Capture login page
                                screenshot_path = await self.screenshot_manager.capture_current_page(
                                    self.page, f"login_page_step_{i}"
                                )
                                if screenshot_path:
                                    results["screenshots"].append(screenshot_path)
                            else:
                                print("  ⚠ Could not find login button - please navigate to login page manually")
                        else:
                            print("  ✓ Login page already visible.")
                            # Capture login page
                            screenshot_path = await self.screenshot_manager.capture_current_page(
                                self.page, f"login_page_step_{i}"
                            )
                            if screenshot_path:
                                results["screenshots"].append(screenshot_path)
                        
                        # Wait for user to complete login (this is the main action for login steps)
                        print("  Waiting for you to complete login...")
                        login_completed = await self.navigator.wait_for_login(timeout=300000)  # 5 minutes
                        
                        if login_completed:
                            print("  ✓ Login completed successfully!")
                            # Wait 5 seconds for page to fully load and settle
                            print("  ⏳ Waiting 5 seconds for page to settle...")
                            await asyncio.sleep(5)
                            
                            # Capture screenshot after login
                            screenshot_path = await self.screenshot_manager.capture_current_page(
                                self.page, f"after_login_step_{i}"
                            )
                            if screenshot_path:
                                results["screenshots"].append(screenshot_path)
                            print("  ✓ Screenshot captured, proceeding to next step...")
                        else:
                            print("  ⚠ Login timeout - proceeding anyway")
                            results["errors"].append(f"Login step may not have completed: {step}")
                        
                        # Continue to next step (loop will automatically continue)
                        continue
                    
                    elif any(word in step_lower for word in ["click", "press", "select", "choose", "open"]):
                        # This is a click action
                        print(f"  🖱️  Detected click action - finding element...")
                        success = await self.navigator.click_element(step, wait_for_state_change=True)
                        
                        if success:
                            # Wait for potential modal/form
                            await self.navigator.wait_for_modal_or_form(timeout=3000)
                            
                            # Capture state after click
                            screenshot_path = await self.screenshot_manager.capture_current_page(
                                self.page, f"after_{step.replace(' ', '_')}"
                            )
                            if screenshot_path:
                                results["screenshots"].append(screenshot_path)
                        else:
                            results["errors"].append(f"Failed to execute step: {step}")
                    
                    elif any(word in step_lower for word in ["fill", "enter", "type", "input", "write"]):
                        # This is a fill action - extract field and value
                        # For now, we'll try to find the field and prompt for value
                        # In a real system, this could be extracted from the step description
                        field_desc = step
                        # Try to extract value from step if mentioned
                        value = self._extract_value_from_step(step)
                        
                        if value:
                            success = await self.navigator.fill_input(field_desc, value)
                            if success:
                                screenshot_path = await self.screenshot_manager.capture_current_page(
                                    self.page, f"filled_{field_desc.replace(' ', '_')}"
                                )
                                if screenshot_path:
                                    results["screenshots"].append(screenshot_path)
                        else:
                            print(f"  Note: Could not extract value for: {step}")
                    
                    elif any(word in step_lower for word in ["wait", "navigate", "go"]):
                        # Navigation or wait step
                        await self.navigator.wait_for_state_change(timeout=2000)
                        screenshot_path = await self.screenshot_manager.capture_current_page(
                            self.page, f"state_{step.replace(' ', '_')}"
                        )
                        if screenshot_path:
                            results["screenshots"].append(screenshot_path)
                    
                    else:
                        # Generic step - try to find and interact
                        success = await self.navigator.click_element(step, wait_for_state_change=True)
                        if success:
                            await self.navigator.wait_for_modal_or_form(timeout=3000)
                            screenshot_path = await self.screenshot_manager.capture_current_page(
                                self.page, f"step_{i}_{step.replace(' ', '_')}"
                            )
                            if screenshot_path:
                                results["screenshots"].append(screenshot_path)
                
                except Exception as e:
                    error_msg = f"Error in step {i} ({step}): {str(e)}"
                    print(f"  ERROR: {error_msg}")
                    results["errors"].append(error_msg)
            
            # Final state capture
            print("\nCapturing final state...")
            await asyncio.sleep(2)
            final_screenshot = await self.screenshot_manager.capture_current_page(
                self.page, "final_state"
            )
            if final_screenshot:
                results["screenshots"].append(final_screenshot)
            
            results["success"] = len(results["errors"]) == 0
            
            print(f"\n{'='*60}")
            print(f"Task completed!")
            print(f"Screenshots captured: {len(results['screenshots'])}")
            print(f"Output directory: {self.screenshot_manager.get_task_directory()}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            error_msg = f"Fatal error executing task: {str(e)}"
            print(f"\nERROR: {error_msg}")
            results["errors"].append(error_msg)
            results["success"] = False
        
        return results
    
    def _extract_value_from_step(self, step: str) -> Optional[str]:
        """Extract a value from step description if mentioned."""
        # Simple extraction - look for quoted text or common patterns
        import re
        
        # Look for quoted values
        quoted = re.search(r'["\']([^"\']+)["\']', step)
        if quoted:
            return quoted.group(1)
        
        # Look for "value: X" pattern
        value_match = re.search(r'value[:\s]+(\w+)', step, re.IGNORECASE)
        if value_match:
            return value_match.group(1)
        
        return None
    
    async def close(self):
        """Close browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        print("Browser closed.")


# Convenience function for synchronous usage
def execute_task_sync(question: str, base_url: Optional[str] = None, headless: bool = False) -> dict:
    """
    Synchronous wrapper for execute_task.
    
    Args:
        question: Natural language question
        base_url: Optional base URL override
        headless: Run in headless mode
        
    Returns:
        Execution results dictionary
    """
    agent = AgentB(headless=headless)
    
    async def run():
        try:
            return await agent.execute_task(question, base_url)
        finally:
            await agent.close()
    
    return asyncio.run(run())

