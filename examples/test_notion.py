"""
Example: Testing Notion workflows with Agent B
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_b import AgentB


async def test_create_database():
    """Test creating a database in Notion."""
    agent = AgentB(headless=False, slow_mo=500)
    
    try:
        result = await agent.execute_task(
            "How do I create a database in Notion?",
            base_url="https://www.notion.so"
        )
        
        print("\nExecution Summary:")
        print(f"Success: {result['success']}")
        print(f"Screenshots: {len(result['screenshots'])}")
        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        
    finally:
        await agent.close()


async def test_filter_database():
    """Test filtering a database in Notion."""
    agent = AgentB(headless=False, slow_mo=500)
    
    try:
        result = await agent.execute_task(
            "How do I filter a database in Notion?",
            base_url="https://www.notion.so"
        )
        
        print("\nExecution Summary:")
        print(f"Success: {result['success']}")
        print(f"Screenshots: {len(result['screenshots'])}")
        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        
    finally:
        await agent.close()


async def main():
    """Run all Notion tests."""
    print("="*60)
    print("Testing Notion Workflows")
    print("="*60)
    
    tests = [
        ("Create Database", test_create_database),
        ("Filter Database", test_filter_database),
    ]
    
    for test_name, test_func in tests:
        print(f"\n\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}\n")
        
        try:
            await test_func()
        except Exception as e:
            print(f"\nTest '{test_name}' failed with error: {e}")
        
        # Wait between tests
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())

