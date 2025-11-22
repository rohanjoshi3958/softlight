#!/usr/bin/env python3
"""
Quick test script to diagnose browser launch issues.
"""
import asyncio
from playwright.async_api import async_playwright


async def test_browser():
    """Test browser launch with different strategies."""
    print("Testing Playwright browser launch...\n")
    
    playwright = await async_playwright().start()
    
    strategies = [
        ("Headless mode", {"headless": True}),
        ("Headless with args", {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}),
        ("Non-headless", {"headless": False}),
        ("Non-headless with args", {"headless": False, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}),
    ]
    
    for name, args in strategies:
        print(f"Trying: {name}...")
        try:
            browser = await playwright.chromium.launch(**args)
            await asyncio.sleep(1)  # Wait to see if it stays alive
            
            # Try to create a context
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("about:blank")
            title = await page.title()
            
            await page.close()
            await context.close()
            await browser.close()
            
            print(f"  ✓ SUCCESS: {name} works!\n")
            await playwright.stop()
            return True
            
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)[:100]}\n")
            continue
    
    print("All strategies failed. Trying Firefox as alternative...")
    try:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("about:blank")
        await page.close()
        await context.close()
        await browser.close()
        print("✓ Firefox works! Consider using Firefox instead.")
        await playwright.stop()
        return True
    except Exception as e:
        print(f"✗ Firefox also failed: {e}")
    
    await playwright.stop()
    return False


if __name__ == "__main__":
    success = asyncio.run(test_browser())
    if not success:
        print("\n" + "="*60)
        print("Browser launch failed. Possible solutions:")
        print("="*60)
        print("1. Reinstall browsers: playwright install chromium --force")
        print("2. Check macOS permissions in System Settings")
        print("3. Try updating Playwright: pip install --upgrade playwright")
        print("4. Use headless mode: python main.py 'question' --headless")
        print("="*60)

