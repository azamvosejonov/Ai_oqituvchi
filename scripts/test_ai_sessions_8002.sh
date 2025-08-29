#!/usr/bin/env bash
set -euo pipefail

BASE="http://0.0.0.0:8002/api/v1"
echo "[1/9] Checking server on $BASE ..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/openapi.json" || true)
echo "OpenAPI status: $CODE"
if [ "$CODE" != "200" ]; then
  echo "Server 8002 da ishlamayotganga o'xshaydi yoki /api/v1/openapi.json mavjud emas."
  exit 1
fi

get_token() {
  local USER="$1"; local PASS="$2"
  curl -s -X POST "$BASE/login/access-token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$USER&password=$PASS" | python3 - <<'PY'
import sys, json
try:
    data=json.load(sys.stdin)
    print(data.get("access_token",""))
except Exception:
    print("")
PY
}

echo "[2/9] Login: trying test@example.com / testpassword"
TOKEN=$(get_token "test@example.com" "testpassword") || true
if [ -z "${TOKEN:-}" ]; then
  echo "[2/9] Fallback: trying admin@example.com / changethis"
  TOKEN=$(get_token "admin@example.com" "changethis") || true
fi
if [ -z "${TOKEN:-}" ]; then
  echo "Token olinmadi. Login ma'lumotlarini tekshiring." >&2
  exit 1
fi
echo "Token OK"

echo "[3/9] Create AI session"
CREATE_RESP=$(curl -s -X POST "$BASE/ai-sessions/sessions?title=CLI%20Test" -H "Authorization: Bearer $TOKEN")
echo "$CREATE_RESP" | sed -E 's/\s+/ /g' | cut -c1-200
SESSION_ID=$(echo "$CREATE_RESP" | python3 - <<'PY'
import sys, json
try:
    print(json.load(sys.stdin).get("id",""))
except Exception:
    print("")
PY
)
if [ -z "${SESSION_ID:-}" ]; then
  echo "Sessiya ID olinmadi" >&2
  exit 1
fi
echo "SESSION_ID=$SESSION_ID"

echo "[4/9] Send text message"
MSG_RESP=$(curl -s -X POST "$BASE/ai-sessions/sessions/$SESSION_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -F "text=Salom, test sessiya uchun matnli xabar." \
  -F "speak=false" \
  -F "language=uz")
echo "$MSG_RESP" | sed -E 's/\s+/ /g' | cut -c1-200

echo "[5/9] Get messages (limit=5)"
MSGS=$(curl -s "$BASE/ai-sessions/sessions/$SESSION_ID/messages?limit=5&offset=0" -H "Authorization: Bearer $TOKEN")
echo "$MSGS" | sed -E 's/\s+/ /g' | cut -c1-200

AUDIO="tests/test_data/test_audio.wav"
if [ -f "$AUDIO" ]; then
  echo "[6/9] Send audio message ($AUDIO)"
  A_RESP=$(curl -s -X POST "$BASE/ai-sessions/sessions/$SESSION_ID/messages" \
    -H "Authorization: Bearer $TOKEN" \
    -F "audio_file=@$AUDIO;type=audio/wav" \
    -F "language=uz" \
    -F "speak=false")
  echo "$A_RESP" | sed -E 's/\s+/ /g' | cut -c1-200
else
  echo "[6/9] Audio fayl topilmadi, bu bosqich o'tkazib yuborildi"
fi

echo "[7/9] Get messages again (limit=5)"
MSGS2=$(curl -s "$BASE/ai-sessions/sessions/$SESSION_ID/messages?limit=5&offset=0" -H "Authorization: Bearer $TOKEN")
echo "$MSGS2" | sed -E 's/\s+/ /g' | cut -c1-200

echo "[8/9] Reset session"
RESET_RESP=$(curl -s -X POST "$BASE/ai-sessions/sessions/$SESSION_ID/reset" -H "Authorization: Bearer $TOKEN")
echo "$RESET_RESP" | sed -E 's/\s+/ /g' | cut -c1-200

echo "[9/9] Delete session"
DEL_RESP=$(curl -s -X DELETE "$BASE/ai-sessions/sessions/$SESSION_ID" -H "Authorization: Bearer $TOKEN")
echo "$DEL_RESP"
