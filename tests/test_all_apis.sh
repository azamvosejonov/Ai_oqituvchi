#!/bin/bash

# Set the base URL
BASE_URL="http://localhost:8002/api/v1"

# Test user credentials
USERNAME="test@example.com"
PASSWORD="testpassword"

# Function to print test header
print_header() {
    echo "\n=== $1 ==="
    echo "----------------------------------------"
}

# Function to make API requests
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local auth_header=$4
    
    echo "[${method}] ${endpoint}"
    if [ -z "$auth_header" ]; then
        curl -s -X ${method} "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            ${data:+-d "$data"} | python3 -m json.tool 2>/dev/null || cat
    else
        curl -s -X ${method} "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${auth_header}" \
            ${data:+-d "$data"} | python3 -m json.tool 2>/dev/null || cat
    fi
    echo "----------------------------------------"
}

# 1. Login and get token
print_header "1. Logging in"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract token using Python
TOKEN=$(python3 -c "
import sys, json
try:
    data = json.loads('''$LOGIN_RESPONSE''')
    print(data.get('access_token', ''))
except:
    print('')
")

if [ -z "$TOKEN" ] || [ "$TOKEN" = "None" ]; then
    echo "Login failed. Exiting..."
    exit 1
fi

# 2. Test User Endpoints
print_header "2. Testing User Endpoints"

# Get current user profile
api_request "GET" "/users/me" "" "$TOKEN"

# 3. Test Interactive Lessons
print_header "3. Testing Interactive Lessons"

# Start a new lesson
LESSON_RESPONSE=$(curl -s -X POST "${BASE_URL}/interactive-lessons/start-lesson" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"lesson_type": "conversation", "topic": "greetings", "difficulty": "beginner", "avatar_type": "default"}')

echo "$LESSON_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LESSON_RESPONSE"

# Extract session ID using Python
SESSION_ID=$(python3 -c "
import sys, json
try:
    data = json.loads('''$LESSON_RESPONSE''')
    print(data.get('id', ''))
except:
    print('')
")

# 4. Test Lesson Interactions
print_header "4. Testing Lesson Interactions"

# Send a message
api_request "POST" "/lesson-interactions/send-message" \
    "{\"session_id\": ${SESSION_ID}, \"message\": \"Salom, qalaysiz?\", \"message_type\": \"text\"}" "$TOKEN"

# 5. Test Words API
print_header "5. Testing Words API"

# Get words list
api_request "GET" "/words/" "" "$TOKEN"

# 6. Test User Progress
print_header "6. Testing User Progress"

# Get user progress
api_request "GET" "/user-progress/me" "" "$TOKEN"

# 7. Test Subscription Plans
print_header "7. Testing Subscription Plans"

# Get available subscription plans
api_request "GET" "/subscription-plans/" "" "$TOKEN"

# 8. Test AI Endpoints
print_header "8. Testing AI Endpoints"

# Get AI models
api_request "GET" "/ai/models" "" "$TOKEN"

# 9. Test Notifications
print_header "9. Testing Notifications"

# Get user notifications
api_request "GET" "/notifications/" "" "$TOKEN"

# 10. Test Tests API
print_header "10. Testing Tests API"

# Get available tests
api_request "GET" "/tests/" "" "$TOKEN"

echo "\n=== API Testing Completed ==="
