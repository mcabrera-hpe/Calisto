"""
Test custom agent creation functionality.
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_custom_agent_api():
    """Test custom agent via API."""
    print("\n1. Testing custom agent via API...")
    
    response = requests.post(
        f"{API_URL}/scenarios/start",
        json={
            "scenario": "Supply chain optimization",
            "client": "Toyota",
            "agents": [
                {
                    "name": "Pinote",
                    "company": "Toyota",
                    "role": "Supply Chain Manager",
                    "objective": "Optimize logistics and reduce costs"
                },
                "Sarah"  # Mix custom and library
            ],
            "max_turns": 1
        },
        stream=True,
        timeout=120
    )
    
    if response.status_code != 200:
        print(f"   ❌ Failed: HTTP {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Check messages
    agents_seen = set()
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                if 'agent' in data:
                    agents_seen.add(data['agent'])
    
    if 'Pinote' in agents_seen and 'Sarah' in agents_seen:
        print(f"   ✅ Custom agent 'Pinote' and library agent 'Sarah' both participated")
        return True
    else:
        print(f"   ❌ Missing agents. Saw: {agents_seen}")
        return False


def test_assistant_custom_agent():
    """Test assistant creating custom agent config."""
    print("\n2. Testing assistant custom agent config generation...")
    
    response = requests.post(
        f"{API_URL}/assistant/chat",
        json={
            "message": "Create custom agent Alex (CTO at Microsoft, objective: evaluate tech solutions) with Yuki for 2-turn cloud discussion",
            "history": []
        },
        timeout=60
    )
    
    # Parse response for config
    config = None
    for line in response.text.split('\n'):
        if 'data:' in line:
            try:
                data = json.loads(line.split('data: ', 1)[1])
                msg = data.get('message', '')
                # Find JSON config in message
                if '"ready"' in msg and '"agents"' in msg:
                    # Extract JSON - find the last complete JSON object
                    start_idx = msg.rfind('{"ready"')
                    if start_idx >= 0:
                        # Find matching closing brace
                        brace_count = 0
                        end_idx = start_idx
                        for i in range(start_idx, len(msg)):
                            if msg[i] == '{':
                                brace_count += 1
                            elif msg[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i + 1
                                    break
                        if end_idx > start_idx:
                            config = json.loads(msg[start_idx:end_idx])
                            break
            except Exception as e:
                print(f"   Debug: Failed to parse: {e}")
                pass
    
    if not config:
        print("   ❌ No config generated")
        return False
    
    # Validate config has custom agent
    if not config.get('agents'):
        print("   ❌ No agents in config")
        return False
    
    has_custom = any(isinstance(a, dict) and a.get('name') == 'Alex' for a in config['agents'])
    has_library = any(a == 'Yuki' for a in config['agents'])
    
    if has_custom and has_library:
        print(f"   ✅ Config has custom agent 'Alex' and library agent 'Yuki'")
        return True
    else:
        print(f"   ❌ Config doesn't have expected agents: {config['agents']}")
        return False


def test_missing_custom_fields():
    """Test validation of incomplete custom agent."""
    print("\n3. Testing validation of incomplete custom agent...")
    
    response = requests.post(
        f"{API_URL}/scenarios/start",
        json={
            "scenario": "Test",
            "client": "Toyota",
            "agents": [
                {
                    "name": "Incomplete",
                    "company": "Test"
                    # Missing role and objective
                }
            ],
            "max_turns": 1
        },
        timeout=10
    )
    
    if response.status_code == 400 and 'missing fields' in response.text.lower():
        print(f"   ✅ Properly rejected incomplete custom agent")
        return True
    else:
        print(f"   ❌ Should have rejected incomplete agent: HTTP {response.status_code}")
        return False


def main():
    """Run all custom agent tests."""
    print("=" * 60)
    print("Custom Agent Creation Tests")
    print("=" * 60)
    
    results = [
        test_custom_agent_api(),
        test_assistant_custom_agent(),
        test_missing_custom_fields()
    ]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CUSTOM AGENT TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
