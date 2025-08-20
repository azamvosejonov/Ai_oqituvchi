import os
import httpx

def run_suite(base):
    print(f"\n===== BASE: {base} =====")
    try:
        with httpx.Client(base_url=base, timeout=30.0, follow_redirects=True) as client:
            # Health
            try:
                r = client.get("/health")
                print("HEALTH", r.status_code, r.text[:120])
            except Exception as e:
                print("HEALTH EXC", e)
                return

            # Login
            token = None
            try:
                data = {"username":"test@example.com","password":"testpassword"}
                lr = client.post("/api/v1/login/access-token", data=data)
                print("LOGIN", lr.status_code, lr.text[:200])
                if lr.status_code == 200:
                    token = lr.json().get("access_token")
            except Exception as e:
                print("LOGIN EXC", e)

            headers = {"Authorization": f"Bearer {token}"} if token else {}

            # TTS
            if token:
                try:
                    tr = client.post("/api/v1/ai/tts", json={"text":"Salom! Sinov ovozi.","language":"uz"}, headers=headers)
                    print("TTS", tr.status_code, tr.text[:200])
                    if tr.status_code == 200 and tr.headers.get('content-type','').startswith('application/json'):
                        audio_url = tr.json().get("audio_url")
                        if audio_url:
                            ar = client.get(audio_url)
                            print("TTS_FILE", ar.status_code, len(ar.content))
                except Exception as e:
                    print("TTS EXC", e)
            else:
                print("TTS SKIP: no token")

            # STT
            if token:
                wav = "tests/test_data/test_audio.wav"
                if os.path.exists(wav):
                    try:
                        with open(wav,"rb") as f:
                            sr = client.post("/api/v1/ai/stt", files={"file": ("test.wav", f, "audio/wav")}, headers=headers)
                            print("STT", sr.status_code, sr.text[:200])
                    except Exception as e:
                        print("STT EXC", e)
                else:
                    print("STT SKIP: missing file")
            else:
                print("STT SKIP: no token")

            # Pronunciation
            if token:
                wav = "tests/test_data/test_audio.wav"
                if os.path.exists(wav):
                    try:
                        with open(wav,"rb") as f:
                            prr = client.post(
                                "/api/v1/ai/pronunciation",
                                data={"reference_text":"Hello, this is a test message"},
                                files={"file": ("test.wav", f, "audio/wav")},
                                headers=headers,
                            )
                            print("PRONUN", prr.status_code, prr.text[:200])
                    except Exception as e:
                        print("PRONUN EXC", e)
                else:
                    print("PRONUN SKIP: missing file")
            else:
                print("PRONUN SKIP: no token")

            # Voice-loop
            if token:
                wav = "tests/test_data/test_audio.wav"
                if os.path.exists(wav):
                    try:
                        with open(wav,"rb") as f:
                            vl = client.post(
                                "/api/v1/ai/voice-loop",
                                data={"language":"uz"},
                                files={"file": ("test.wav", f, "audio/wav")},
                                headers=headers,
                            )
                            print("VOICE_LOOP", vl.status_code, vl.text[:200])
                    except Exception as e:
                        print("VOICE_LOOP EXC", e)
                else:
                    print("VOICE_LOOP SKIP: missing file")
            else:
                print("VOICE_LOOP SKIP: no token")

            # Suggested lessons
            if token:
                try:
                    s = client.get("/api/v1/ai/lessons/suggested", headers=headers)
                    print("SUGGESTED", s.status_code, s.text[:200])
                except Exception as e:
                    print("SUGGESTED EXC", e)
            else:
                print("SUGGESTED SKIP: no token")
    except Exception as e:
        print("BASE EXC", e)

if __name__ == "__main__":
    for base in ("http://0.0.0.0:8004", "http://0.0.0.0:8004"):
        run_suite(base)
