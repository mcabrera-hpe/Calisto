"""
Test script for Callisto FastAPI backend.

Run this inside the API container to verify endpoints work.
"""

import requests
import json
import time

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("✅ Health check passed")


def test_create_conversation():
    """Test creating a conversation."""
    print("\nTesting conversation creation...")
    response = requests.post(
        f"{API_URL}/conversations",
        json={
            "scenario": "Test negotiation",
            "client": "Toyota",
            "num_agents": 2,
            "max_turns": 2
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    conv_id = data["conversation_id"]
    print(f"✅ Conversation created: {conv_id}")
    return conv_id


def test_get_conversation(conv_id):
    """Test getting conversation details."""
    print(f"\nTesting conversation retrieval...")
    response = requests.get(f"{API_URL}/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "Test negotiation"
    assert data["client"] == "Toyota"
    print("✅ Conversation retrieval passed")


def test_stream_conversation(conv_id):
    """Test streaming conversation."""
    print(f"\nTesting conversation streaming...")
    response = requests.post(
        f"{API_URL}/conversations/{conv_id}/start",
        stream=True
    )
    assert response.status_code == 200
    
    message_count = 0
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                message = json.loads(line_str[6:])
                if 'error' not in message:
                    message_count += 1
                    print(f"  Received message from {message.get('agent', 'unknown')}")
    
    print(f"✅ Streaming test passed - received {message_count} messages")
    return message_count


def test_delete_conversation(conv_id):
    """Test deleting a conversation."""
    print(f"\nTesting conversation deletion...")
    response = requests.delete(f"{API_URL}/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    print("✅ Deletion passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Callisto API Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_health()
        conv_id = test_create_conversation()
        test_get_conversation(conv_id)
        message_count = test_stream_conversation(conv_id)
        
        # Verify messages were stored
        response = requests.get(f"{API_URL}/conversations/{conv_id}")
        final_data = response.json()
        assert len(final_data["messages"]) == message_count
        
        test_delete_conversation(conv_id)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API request failed: {e}")
        print("Make sure the API service is running on port 8000")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
