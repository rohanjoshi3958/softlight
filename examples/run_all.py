"""
Run all example workflows
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import test_linear
import test_notion


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AGENT B - Complete Test Suite")
    print("="*60 + "\n")
    
    # Run Linear tests
    await test_linear.main()
    
    # Wait before switching apps
    print("\n\nWaiting 5 seconds before switching to Notion...\n")
    await asyncio.sleep(5)
    
    # Run Notion tests
    await test_notion.main()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

