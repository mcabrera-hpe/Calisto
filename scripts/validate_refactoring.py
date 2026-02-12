#!/usr/bin/env python3
"""
Validate that code refactoring works correctly.

Run: docker-compose exec app python scripts/validate_refactoring.py
"""

import sys
import traceback

def main() -> None:
    """Run validation tests for the refactored code."""
    print("=" * 60)
    print("VALIDATING CODE REFACTORING")
    print("=" * 60)
    
    # Test 1: Import from core.py (backwards compatibility)
    try:
        from agents.core import Agent, HumanAgent, MultiAgentOrchestrator
        print("✅ Test 1: Backwards compatibility imports work")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        print("\nFull traceback:", flush=True)
        for line in traceback.format_exc().splitlines():
            print(line, flush=True)
        sys.stdout.flush()
        return
    
    # Test 2: Import from new files directly
    try:
        from agents.base import Agent as BaseAgent, HumanAgent as BaseHuman
        from agents.orchestrator import MultiAgentOrchestrator as Orch
        print("✅ Test 2: Direct imports from base.py and orchestrator.py work")
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return
    
    # Test 3: Verify classes are the same
    try:
        assert Agent is BaseAgent, "Agent classes should be identical"
        assert HumanAgent is BaseHuman, "HumanAgent classes should be identical"
        assert MultiAgentOrchestrator is Orch, "Orchestrator classes should be identical"
        print("✅ Test 3: Re-exported classes are identical to source classes")
    except AssertionError as e:
        print(f"❌ Test 3 FAILED: {e}")
        return
    
    # Test 4: Create agent instances
    try:
        agent = Agent(
            name="TestAgent", 
            role="Tester", 
            company="TestCo",
            objective="Test the system",
            model="mistral"
        )
        print(f"✅ Test 4: Agent instance created: {agent.name}")
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        return
    
    # Test 5: Verify agent has new helper methods
    try:
        assert hasattr(agent, "_build_messages"), "Agent should have _build_messages method"
        assert hasattr(agent, "_call_llm_api"), "Agent should have _call_llm_api method"
        assert hasattr(agent, "_build_system_prompt"), "Agent should have _build_system_prompt method"
        print("✅ Test 5: Agent has extracted helper methods")
    except AssertionError as e:
        print(f"❌ Test 5 FAILED: {e}")
        return
    
    # Test 6: Verify orchestrator has new helper methods
    try:
        agents = [agent]
        orch = MultiAgentOrchestrator(agents=agents)
        assert hasattr(orch, "_add_initial_message"), "Orchestrator should have _add_initial_message"
        assert hasattr(orch, "_execute_turn"), "Orchestrator should have _execute_turn"
        assert hasattr(orch, "_should_terminate"), "Orchestrator should have _should_terminate"
        print("✅ Test 6: Orchestrator has extracted helper methods")
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! Code refactoring is working correctly.")
    print("=" * 60)

if __name__ == "__main__":
    main()
