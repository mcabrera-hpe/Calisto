"""
End-to-end test for the conversational UI workflow.

This script simulates the full user journey:
1. Chat with Grid assistant to configure scenario
2. Assistant suggests agents
3. User confirms configuration
4. Start scenario with selected agents
"""

import os
import sys
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

API_URL = os.getenv("API_URL", "http://localhost:8000")


def test_full_workflow():
    """Test the complete conversational workflow."""
    print("\n" + "="*60)
    print("End-to-End Conversational Workflow Test")
    print("="*60 + "\n")
    
    # Step 1: Initial message to assistant
    print("Step 1: User asks about scenario")
    print("-" * 40)
    response = requests.post(
        f"{API_URL}/assistant/chat",
        json={
            "message": "I want to simulate a server purchase negotiation with Toyota",
            "history": []
        },
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        return False
    
    # Parse assistant response
    assistant_msg_1 = None
    for line in response.text.strip().split('\n'):
        if line.startswith('data: '):
            data = json.loads(line[6:])
            assistant_msg_1 = data.get('message', '')
            print(f"Assistant: {assistant_msg_1[:100]}...")
            break
    
    if not assistant_msg_1:
        print("❌ FAILED: No assistant response")
        return False
    
    print("✅ Assistant responded\n")
    
    # Step 2: User confirms agents
    print("Step 2: User confirms agent selection")
    print("-" * 40)
    
    history = [
        {"role": "user", "content": "I want to simulate a server purchase negotiation with Toyota"},
        {"role": "assistant", "content": assistant_msg_1}
    ]
    
    response = requests.post(
        f"{API_URL}/assistant/chat",
        json={
            "message": "Yes, those agents look perfect. Let's use them for a 3-turn negotiation.",
            "history": history
        },
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        return False
    
    # Parse assistant response and look for JSON config
    assistant_msg_2 = None
    config = None
    for line in response.text.strip().split('\n'):
        if line.startswith('data: '):
            data = json.loads(line[6:])
            assistant_msg_2 = data.get('message', '')
            print(f"Assistant: {assistant_msg_2[:100]}...")
            
            # Extract JSON config
            if '{' in assistant_msg_2 and '}' in assistant_msg_2:
                try:
                    start = assistant_msg_2.index('{')
                    end = assistant_msg_2.rindex('}') + 1
                    config = json.loads(assistant_msg_2[start:end])
                except:
                    pass
            break
    
    if not config or not config.get('ready'):
        print("❌ FAILED: No valid config generated")
        print(f"Config: {config}")
        return False
    
    print(f"✅ Config generated: {config}\n")
    
    # Step 3: Start scenario with selected agents
    print("Step 3: Start scenario simulation")
    print("-" * 40)
    
    response = requests.post(
        f"{API_URL}/scenarios/start",
        json={
            "scenario": config['scenario'],
            "client": config['client'],
            "agents": config['agents'],
            "max_turns": min(config['max_turns'], 2)  # Limit to 2 for testing
        },
        stream=True,
        timeout=120
    )
    
    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        return False
    
    # Count messages
    message_count = 0
    agent_names = set()
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                if 'agent' in data:
                    message_count += 1
                    agent_names.add(data['agent'])
                    print(f"  Turn {data.get('turn')}: {data['agent']} speaking...")
    
    print(f"\n✅ Scenario completed: {message_count} messages from {len(agent_names)} agents\n")
    
    if message_count >= 2:
        print("="*60)
        print("✅ END-TO-END TEST PASSED")
        print("="*60)
        return True
    else:
        print("❌ FAILED: Expected at least 2 messages")
        return False


def main():
    """Run the end-to-end test."""
    try:
        success = test_full_workflow()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
