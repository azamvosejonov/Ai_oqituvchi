import io
from pathlib import Path

import pytest
from app.core.config import settings


BASE = f"{settings.API_V1_STR}/ai"
DATA_DIR = Path(__file__).parent.parent / "test_data"
AUDIO_PATH = DATA_DIR / "test_audio.wav"


def test_list_tts_voices(client):
    r = client.get(f"{BASE}/tts/voices")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "voices" in data and isinstance(data["voices"], list)


def test_list_stt_languages(client):
    r = client.get(f"{BASE}/stt/languages")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "languages" in data and isinstance(data["languages"], list)


def test_ai_ask_text_only(client, power_user_token_headers):
    payload = {"prompt": "Salom, bu test!"}
    r = client.post(f"{BASE}/ask", json=payload, headers=power_user_token_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "text" in data


def test_tts_stream(client, power_user_token_headers):
    payload = {"text": "Hello world", "language": "en"}
    r = client.post(f"{BASE}/tts", json=payload, headers=power_user_token_headers)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("audio/mpeg")
    # StreamingResponse content is aggregated by TestClient
    assert r.content and len(r.content) > 0


def test_analyze_answer(client):
    payload = {"user_response": "hello", "reference_text": "hello", "language": "en"}
    r = client.post(f"{BASE}/analyze-answer", json=payload)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)


@pytest.mark.skipif(not AUDIO_PATH.exists(), reason="Audio test file missing")
def test_stt_transcription(client, power_user_token_headers):
    with open(AUDIO_PATH, "rb") as f:
        files = {"file": ("test_audio.wav", f, "audio/wav")}
        r = client.post(f"{BASE}/stt", files=files, headers=power_user_token_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict) and "text" in data


@pytest.mark.skipif(not AUDIO_PATH.exists(), reason="Audio test file missing")
def test_pronunciation_assessment(client, power_user_token_headers):
    with open(AUDIO_PATH, "rb") as f:
        files = {"file": ("test_audio.wav", f, "audio/wav")}
        data = {"reference_text": "Hello, this is a test message"}
        r = client.post(f"{BASE}/pronunciation", files=files, data=data, headers=power_user_token_headers)
    assert r.status_code == 200
    resp = r.json()
    assert isinstance(resp, dict)
    # Be flexible about exact keys; current schema returns accuracy_score, allow common variants too
    assert any(k in resp for k in ["accuracy_score", "score", "accuracy", "feedback", "transcribed_text"])


@pytest.mark.skipif(not AUDIO_PATH.exists(), reason="Audio test file missing")
def test_voice_loop(client, power_user_token_headers):
    with open(AUDIO_PATH, "rb") as f:
        files = {"file": ("test_audio.wav", f, "audio/wav")}
        data = {"language": "en", "reference_text": "Hello, this is a test message"}
        r = client.post(f"{BASE}/voice-loop", files=files, data=data, headers=power_user_token_headers)
    assert r.status_code == 200
    resp = r.json()
    assert isinstance(resp, dict)
    # Expect core fields present in voice loop response
    assert any(k in resp for k in ["text", "transcript"])  # AI text or transcript present
    # audio TTS may be skipped if quota insufficient; only check key existence when present
    # If present, audio_url should be a string path
    if "audio_url" in resp and resp["audio_url"] is not None:
        assert isinstance(resp["audio_url"], str) and len(resp["audio_url"]) > 0


def test_pronunciation_history_and_summary(client, power_user_token_headers):
    r1 = client.get(f"{BASE}/pronunciation/history", headers=power_user_token_headers)
    assert r1.status_code == 200
    assert isinstance(r1.json(), list)

    r2 = client.get(f"{BASE}/pronunciation/summary", headers=power_user_token_headers)
    assert r2.status_code == 200
    assert isinstance(r2.json(), dict)
