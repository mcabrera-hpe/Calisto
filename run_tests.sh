#!/bin/bash
# Run all Callisto tests
# Usage: ./run_tests.sh

set -e  # Exit on error

echo "============================================================"
echo "Callisto Test Suite"
echo "============================================================"
echo ""

# Check Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Containers not running. Starting them now..."
    docker-compose up -d
    sleep 5
fi

echo "✅ Docker containers are running"
echo ""

# Check proxy is running
if ! curl -s http://localhost:9001/health &> /dev/null; then
    echo "⚠️  WARNING: Proxy server not running on port 9001"
    echo "   Some tests may fail without the proxy."
    echo "   Start it with: python3 proxy_server.py"
    echo ""
fi

# Test 1: Code validation
echo ">>> Test 1: Code Structure Validation"
echo "============================================================"
docker-compose exec -T app python scripts/validate_refactoring.py
echo ""

# Test 2: API Quick Tests (no LLM needed)
echo ">>> Test 2: API Quick Integration Tests"
echo "============================================================"
docker-compose exec -T api python scripts/test_api_quick.py
echo ""

# Test 3: Full API Tests (requires proxy + LLM)
echo ">>> Test 3: Full API Tests (with LLM streaming)"
echo "============================================================"
echo "⚠️  This test requires the proxy server running on port 9001"
echo "   and will make actual LLM API calls."
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose exec -T api python scripts/test_api.py || echo "⚠️  Test failed - may need proxy server"
else
    echo "Skipped."
fi
echo ""

# Test 4: Agent Conversation Test (requires proxy + LLM)
echo ">>> Test 4: Agent Conversation Test"
echo "============================================================"
echo "⚠️  This test requires the proxy server running on port 9001"
echo "   and will make actual LLM API calls."
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose exec -T app python scripts/test_agents.py || echo "⚠️  Test failed - may need proxy server"
else
    echo "Skipped."
fi
echo ""

echo "============================================================"
echo "Test Suite Complete"
echo "============================================================"
