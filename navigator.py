"""
Navigator: Handles finding and interacting with UI elements dynamically.
"""
import asyncio
from typing import Optional, List, Dict
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class Navigator:
    """Handles dynamic navigation and element finding in web applications."""
    
    def __init__(self, page: Page):
        self.page = page
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def find_element_by_description(self, description: str, timeout: int = 10000) -> Optional[Dict]:
        """
        Find an element based on a natural language description.
        
        Args:
            description: Description of what to find (e.g., "Create Project button", "filter input field")
            timeout: Maximum time to wait in milliseconds
            
        Returns:
            Dictionary with element info or None if not found
        """
        # Try multiple strategies to find the element
        strategies = [
            self._find_by_text_content,
            self._find_by_aria_label,
            self._find_by_role,
            self._find_by_placeholder,
            self._find_by_semantic_meaning,
        ]
        
        for strategy in strategies:
            try:
                element = await strategy(description, timeout)
                if element:
                    return element
            except Exception as e:
                continue
        
        return None
    
    async def _find_by_text_content(self, description: str, timeout: int) -> Optional[Dict]:
        """Find element by matching text content."""
        # Extract key words from description
        keywords = self._extract_keywords(description)
        
        for keyword in keywords:
            try:
                # Try exact text match
                selector = f"text='{keyword}'"
                element = await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
                if element:
                    return {"element": element, "selector": selector, "method": "text_content"}
            except:
                pass
            
            try:
                # Try case-insensitive partial match using get_by_text
                element = await self.page.get_by_text(keyword, exact=False).first.wait_for(
                    state="visible", timeout=timeout
                )
                if element:
                    return {"element": element, "selector": f"text={keyword}", "method": "text_content"}
            except:
                pass
        
        return None
    
    async def _find_by_aria_label(self, description: str, timeout: int) -> Optional[Dict]:
        """Find element by aria-label attribute."""
        keywords = self._extract_keywords(description)
        
        for keyword in keywords:
            try:
                selector = f"[aria-label*='{keyword}' i]"
                element = await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
                if element:
                    return {"element": element, "selector": selector, "method": "aria_label"}
            except:
                pass
        
        return None
    
    async def _find_by_role(self, description: str, timeout: int) -> Optional[Dict]:
        """Find element by ARIA role and accessible name."""
        # Map common descriptions to roles
        role_map = {
            "button": ["button", "link"],
            "input": ["textbox", "searchbox"],
            "field": ["textbox", "combobox"],
            "menu": ["menu", "menubar"],
            "modal": ["dialog"],
            "form": ["form"],
        }
        
        description_lower = description.lower()
        keywords = self._extract_keywords(description)
        
        for keyword in keywords:
            for role_type, roles in role_map.items():
                if role_type in description_lower:
                    for role in roles:
                        try:
                            # Try to find by role with accessible name
                            element = await self.page.get_by_role(role, name=keyword, exact=False).first.wait_for(
                                state="visible", timeout=timeout
                            )
                            if element:
                                return {"element": element, "selector": f"role={role}", "method": "role"}
                        except:
                            pass
        
        return None
    
    async def _find_by_placeholder(self, description: str, timeout: int) -> Optional[Dict]:
        """Find input elements by placeholder text."""
        keywords = self._extract_keywords(description)
        
        for keyword in keywords:
            try:
                selector = f"input[placeholder*='{keyword}' i], textarea[placeholder*='{keyword}' i]"
                element = await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
                if element:
                    return {"element": element, "selector": selector, "method": "placeholder"}
            except:
                pass
        
        return None
    
    async def _find_by_semantic_meaning(self, description: str, timeout: int) -> Optional[Dict]:
        """Use LLM to generate better selectors based on semantic understanding."""
        try:
            # Get page content for context
            page_content = await self.page.content()
            # Limit content size for API
            page_content = page_content[:5000]
            
            prompt = f"""Given this HTML snippet and a description "{description}", suggest the best CSS selector or XPath to find the element.

HTML snippet:
{page_content[:2000]}

Description: {description}

Return only a CSS selector or XPath, nothing else."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a web automation expert. Return only CSS selectors or XPath expressions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            selector = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            selector = selector.replace("```", "").strip()
            
            if selector:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
                    if element:
                        return {"element": element, "selector": selector, "method": "semantic"}
                except:
                    pass
        except Exception as e:
            pass
        
        return None
    
    def _extract_keywords(self, description: str) -> List[str]:
        """Extract relevant keywords from description."""
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "how", "do", "i"}
        words = description.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Also try multi-word phrases
        if len(keywords) > 1:
            # Add 2-word combinations
            for i in range(len(keywords) - 1):
                keywords.append(f"{keywords[i]} {keywords[i+1]}")
        
        return keywords
    
    async def click_element(self, description: str, wait_for_state_change: bool = True) -> bool:
        """
        Find and click an element based on description.
        
        Args:
            description: Description of element to click
            wait_for_state_change: Whether to wait for UI state change after clicking
            
        Returns:
            True if successful, False otherwise
        """
        element_info = await self.find_element_by_description(description)
        
        if not element_info:
            print(f"Could not find element: {description}")
            return False
        
        try:
            element = element_info["element"]
            
            # Scroll element into view
            await element.scroll_into_view_if_needed()
            
            # Click the element
            await element.click()
            
            if wait_for_state_change:
                # Wait a bit for UI to update
                await self.page.wait_for_timeout(1000)
            
            print(f"Successfully clicked: {description}")
            return True
            
        except Exception as e:
            print(f"Error clicking element {description}: {e}")
            return False
    
    async def fill_input(self, description: str, value: str) -> bool:
        """
        Find and fill an input field.
        
        Args:
            description: Description of input field
            value: Value to fill in
            
        Returns:
            True if successful, False otherwise
        """
        element_info = await self.find_element_by_description(description)
        
        if not element_info:
            print(f"Could not find input: {description}")
            return False
        
        try:
            element = element_info["element"]
            await element.scroll_into_view_if_needed()
            await element.fill(value)
            print(f"Successfully filled {description} with: {value}")
            return True
        except Exception as e:
            print(f"Error filling input {description}: {e}")
            return False
    
    async def wait_for_modal_or_form(self, timeout: int = 5000) -> bool:
        """
        Wait for a modal or form to appear.
        
        Returns:
            True if modal/form appeared, False otherwise
        """
        try:
            # Common selectors for modals and forms
            modal_selectors = [
                "[role='dialog']",
                ".modal",
                "[class*='modal']",
                "[class*='dialog']",
                "[class*='overlay']",
            ]
            
            for selector in modal_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=timeout, state="visible")
                    return True
                except:
                    continue
            
            # Also wait a bit for any UI changes
            await self.page.wait_for_timeout(1000)
            return True
            
        except Exception as e:
            return False
    
    async def wait_for_state_change(self, timeout: int = 3000) -> bool:
        """Wait for any UI state change."""
        try:
            await self.page.wait_for_timeout(timeout)
            return True
        except:
            return False

