"""
Test script for new conversational endpoints.

Tests the assistant chat and scenario start endpoints.
"""

import os
import sys
import requests
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

API_URL = os.getenv("API_URL", "http://localhost:8000")


def test_assistant_chat():
    """Test the assistant chat endpoint."""
    print("Testing assistant chat endpoint...", end=" ")
    
    response = requests.post(
        f"{API_URL}/assistant/chat",
        json={
            "message": "I want to simulate a server purchase negotiation with Toyota",
            "history": []
        },
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"FAILED (status {response.status_code})")
        return False
    
    # Parse SSE stream
    lines = response.text.strip().split('\n')
    found_message = False
    for line in lines:
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if 'message' in data and len(data['message']) > 0:
                found_message = True
                break
    
    if found_message:
        print("PASSED ✅")
        return True
    else:
        print("FAILED (no message in response)")
        return False


def test_scenario_start():
    """Test the scenario start endpoint."""
    print("Testing scenario start endpoint...", end=" ")
    
    response = requests.post(
        f"{API_URL}/scenarios/start",
        json={
            "scenario": "Test server negotiation",
            "client": "Toyota",
            "agents": ["Sarah", "Yuki"],
            "max_turns": 1
        },
        stream=True,
        timeout=120
    )
    
    if response.status_code != 200:
        print(f"FAILED (status {response.status_code})")
        return False
    
    # Check we get at least one message
    message_count = 0
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                if 'agent' in data and 'message' in data:
                    message_count += 1
    
    if message_count >= 1:
        print(f"PASSED ✅ ({message_count} messages)")
        return True
    else:
        print(f"FAILED (only {message_count} messages)")
        return False


def test_invalid_agent():
    """Test scenario start with invalid agent name."""
    print("Testing invalid agent handling...", end=" ")
    
    response = requests.post(
        f"{API_URL}/scenarios/start",
        json={
            "scenario": "Test",
            "client": "Toyota",
            "agents": ["InvalidAgent"],
            "max_turns": 1
        },
        timeout=10
    )
    
    if response.status_code == 400:
        print("PASSED ✅")
        return True
    else:
        print(f"FAILED (expected 400, got {response.status_code})")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("The Grid - New Endpoints Test")
    print("="*60)
    
    results = []
    
    # Test assistant chat
    results.append(test_assistant_chat())
    
    # Test scenario start (requires LLM)
    if os.getenv("LLM_API_TOKEN"):
        results.append(test_scenario_start())
    else:
        print("Skipping scenario start test (no LLM_API_TOKEN)")
    
    # Test error handling
    results.append(test_invalid_agent())
    
    print("="*60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
