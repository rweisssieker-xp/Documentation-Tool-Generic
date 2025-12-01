#!/usr/bin/env python3
"""
Autonomous Agent Demo
Demonstrates autonomous documentation agent capabilities.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import AutonomousAgent


def main():
    print("=" * 60)
    print("Autonomous Documentation Agent - Demo")
    print("=" * 60)
    
    agent = AutonomousAgent()
    
    print(f"\nAgent Status:")
    print(f"  Tools Available: {agent.tool_executor.available}")
    print(f"  AI Available: {agent.client is not None}")
    print(f"  Model: {agent.model}")
    
    if not agent.client:
        print("\n[WARNING] OpenAI API Key not set. Agent requires AI.")
        print("Set OPENAI_API_KEY environment variable to enable agent.")
        return
    
    # Demo goal
    goal = "Dokumentiere den Login-Prozess einer Web-Anwendung"
    
    print(f"\nGoal: {goal}")
    print(f"Max Steps: 5 (demo mode)")
    print("-" * 60)
    
    # Execute task (limited steps for demo)
    try:
        steps = agent.execute_task(goal, max_steps=5)
        
        print(f"\nExecution Summary:")
        print(f"  Steps Executed: {len(steps)}")
        
        for i, step in enumerate(steps, 1):
            print(f"\n  Step {i}:")
            print(f"    Action: {step.get('action', 'N/A')}")
            print(f"    Parameters: {step.get('parameters', {})}")
            print(f"    Success: {step.get('success', False)}")
            if step.get('result'):
                result = str(step['result'])[:50]
                print(f"    Result: {result}...")
        
        print("\n" + "=" * 60)
        print("[OK] Agent demo completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Agent execution failed: {e}")
        print("\nNote: Agent requires:")
        print("  - OpenAI API Key (OPENAI_API_KEY)")
        print("  - pyautogui for tool execution")
        print("  - Access to target application")


if __name__ == "__main__":
    main()

