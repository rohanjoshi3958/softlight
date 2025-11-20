"""
Main entry point for Agent B
"""
import asyncio
import argparse
from agent_b import AgentB


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agent B: Web automation and screenshot capture system"
    )
    parser.add_argument(
        "question",
        type=str,
        help="Natural language question (e.g., 'How do I create a project in Linear?')"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Base URL to override parsed URL"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=500,
        help="Slow down operations by milliseconds (default: 500)"
    )
    
    args = parser.parse_args()
    
    agent = AgentB(headless=args.headless, slow_mo=args.slow_mo)
    
    try:
        result = await agent.execute_task(args.question, base_url=args.url)
        
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"Question: {result['question']}")
        print(f"App: {result['workflow']['app_name']}")
        print(f"Action: {result['workflow']['action']}")
        print(f"Success: {result['success']}")
        print(f"Screenshots captured: {len(result['screenshots'])}")
        print(f"Output directory: {agent.screenshot_manager.get_task_directory()}")
        
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("="*60)
        
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())

