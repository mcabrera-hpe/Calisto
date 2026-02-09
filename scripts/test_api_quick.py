"""
Quick integration test for Callisto API endpoints.

Tests API structure without waiting for full LLM responses.
"""

import requests
import json

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("✅ Testing health endpoint...", end=" ")
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Callisto API"
    print("PASSED")


def test_create_conversation():
    """Test creating a conversation."""
    print("✅ Testing conversation creation...", end=" ")
    response = requests.post(
        f"{API_URL}/conversations",
        json={
            "scenario": "Quick integration test",
            "client": "Toyota",
            "num_agents": 2,
            "max_turns": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    conv_id = data["conversation_id"]
    print(f"PASSED (ID: {conv_id[:8]}...)")
    return conv_id


def test_get_conversation(conv_id):
    """Test getting conversation details."""
    print("✅ Testing conversation retrieval...", end=" ")
    response = requests.get(f"{API_URL}/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "Quick integration test"
    assert data["client"] == "Toyota"
    assert data["status"] == "created"
    print("PASSED")


def test_delete_conversation(conv_id):
    """Test deleting a conversation."""
    print("✅ Testing conversation deletion...", end=" ")
    response = requests.delete(f"{API_URL}/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    print("PASSED")


def test_404():
    """Test 404 for non-existent conversation."""
    print("✅ Testing 404 handling...", end=" ")
    response = requests.get(f"{API_URL}/conversations/nonexistent-id")
    assert response.status_code == 404
    print("PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("Callisto API Quick Integration Test")
    print("=" * 60)
    
    try:
        test_health()
        conv_id = test_create_conversation()
        test_get_conversation(conv_id)
        test_delete_conversation(conv_id)
        test_404()
        
        print("\n" + "=" * 60)
        print("✅ ALL QUICK TESTS PASSED")
        print("=" * 60)
        print("\nNote: Full conversation streaming not tested (requires LLM)")
        
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
