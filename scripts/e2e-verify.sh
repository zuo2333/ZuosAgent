#!/bin/bash
# End-to-End Verification Script for LLM Chat Application
# Run this script after starting the application with docker-compose up -d

set -e

echo "=== LLM Chat Application E2E Verification ==="
echo ""

# Configuration
API_BASE="${API_BASE:-http://localhost:8001}"
FRONTEND_BASE="${FRONTEND_BASE:-http://localhost:5173}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

check_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((pass_count++))
}

check_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((fail_count++))
}

# 1. Health Check
echo "1. Checking Health Endpoints..."

# Backend health
if curl -sf "${API_BASE}/health" > /dev/null 2>&1; then
    check_pass "Backend health check"
else
    check_fail "Backend health check"
fi

# Root endpoint
if curl -sf "${API_BASE}/" > /dev/null 2>&1; then
    check_pass "Backend root endpoint"
else
    check_fail "Backend root endpoint"
fi

# Frontend
if curl -sf "${FRONTEND_BASE}/" > /dev/null 2>&1; then
    check_pass "Frontend accessible"
else
    check_fail "Frontend accessible"
fi

echo ""

# 2. API Endpoints
echo "2. Testing API Endpoints..."

# Create session
SESSION_RESPONSE=$(curl -sf -X POST "${API_BASE}/api/sessions" \
    -H "Content-Type: application/json" \
    -d '{"name": "E2E Test Session"}')

if [ $? -eq 0 ] && echo "$SESSION_RESPONSE" | grep -q "id"; then
    check_pass "Create session"
    SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
else
    check_fail "Create session"
    SESSION_ID=""
fi

# List sessions
if curl -sf "${API_BASE}/api/sessions" > /dev/null 2>&1; then
    check_pass "List sessions"
else
    check_fail "List sessions"
fi

# Get session
if [ -n "$SESSION_ID" ]; then
    if curl -sf "${API_BASE}/api/sessions/${SESSION_ID}" > /dev/null 2>&1; then
        check_pass "Get session by ID"
    else
        check_fail "Get session by ID"
    fi
else
    check_fail "Get session by ID (no session ID)"
fi

# Update session
if [ -n "$SESSION_ID" ]; then
    if curl -sf -X PUT "${API_BASE}/api/sessions/${SESSION_ID}" \
        -H "Content-Type: application/json" \
        -d '{"name": "Updated E2E Session"}' > /dev/null 2>&1; then
        check_pass "Update session"
    else
        check_fail "Update session"
    fi
else
    check_fail "Update session (no session ID)"
fi

# Create provider
PROVIDER_RESPONSE=$(curl -sf -X POST "${API_BASE}/api/providers" \
    -H "Content-Type: application/json" \
    -d '{"name": "E2E Test Provider", "provider_type": "openai"}')

if [ $? -eq 0 ] && echo "$PROVIDER_RESPONSE" | grep -q "id"; then
    check_pass "Create provider"
    PROVIDER_ID=$(echo "$PROVIDER_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
else
    check_fail "Create provider"
    PROVIDER_ID=""
fi

# List providers
if curl -sf "${API_BASE}/api/providers" > /dev/null 2>&1; then
    check_pass "List providers"
else
    check_fail "List providers"
fi

# Get global config
if curl -sf "${API_BASE}/api/config" > /dev/null 2>&1; then
    check_pass "Get global config"
else
    check_fail "Get global config"
fi

echo ""

# 3. Cleanup
echo "3. Cleaning up test data..."

# Delete test session
if [ -n "$SESSION_ID" ]; then
    if curl -sf -X DELETE "${API_BASE}/api/sessions/${SESSION_ID}" > /dev/null 2>&1; then
        check_pass "Delete session"
    else
        check_fail "Delete session"
    fi
else
    check_fail "Delete session (no session ID)"
fi

# Delete test provider
if [ -n "$PROVIDER_ID" ]; then
    if curl -sf -X DELETE "${API_BASE}/api/providers/${PROVIDER_ID}" > /dev/null 2>&1; then
        check_pass "Delete provider"
    else
        check_fail "Delete provider"
    fi
else
    check_fail "Delete provider (no provider ID)"
fi

echo ""

# 4. Docker Health Checks
echo "4. Checking Docker Containers..."

if docker ps --format '{{.Names}}' | grep -q "llm-chat-postgres"; then
    if docker ps --format '{{.Status}}' | grep "llm-chat-postgres" | grep -q "healthy"; then
        check_pass "PostgreSQL container healthy"
    else
        check_pass "PostgreSQL container running"
    fi
else
    check_fail "PostgreSQL container"
fi

if docker ps --format '{{.Names}}' | grep -q "llm-chat-backend"; then
    check_pass "Backend container running"
else
    check_fail "Backend container"
fi

if docker ps --format '{{.Names}}' | grep -q "llm-chat-frontend"; then
    check_pass "Frontend container running"
else
    check_fail "Frontend container"
fi

echo ""

# Summary
echo "=== Summary ==="
echo -e "${GREEN}Passed: ${pass_count}${NC}"
echo -e "${RED}Failed: ${fail_count}${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Some checks failed. Please review the output above.${NC}"
    exit 1
fi
