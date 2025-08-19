import requests
import json

# --- Konfiguratsiya ---
BASE_URL = "http://0.0.0.0:8004/api/v1"
# Iltimos, init_db.py skriptida yaratilgan test foydalanuvchi ma'lumotlarini kiriting
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword"
# ---

def get_access_token():
    """Tizimga kirib, access token oladi."""
    print("--- Tizimga kirish ---")
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    try:
        response = requests.post(f"{BASE_URL}/login/access-token", data=login_data, timeout=20)
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Muvaffaqiyatli kirildi.")
            return tokens["access_token"]
        else:
            print(f"❌ Login xatosi: {response.status_code} {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Serverga ulanishda xatolik: {e}")
        print("Iltimos, server ishlayotganiga ishonch hosil qiling.")
        return None

def test_endpoint(method, endpoint, token, json_data=None, files=None, data=None, params=None):
    """Umumiy endpoint test funksiyasi."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n--- Test: {method.upper()} {url} ---")
    
    try:
        if method.lower() == 'post':
            response = requests.post(url, headers=headers, json=json_data, files=files, data=data, timeout=30)
        elif method.lower() == 'get':
            response = requests.get(url, headers=headers, params=params, timeout=30)
        else:
            print(f"Qo'llab-quvvatlanmaydigan metod: {method}")
            return

        if response.status_code == 200:
            print(f"✅ Muvaffaqiyatli (Status: {response.status_code})")
            # print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Xatolik (Status: {response.status_code})")
            print(f"Javob: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ So'rovda xatolik: {e}")


def test_ai_assistant_endpoints(token):
    print("\n========================================")
    print("   AI Assistant Endpointlari Testi")
    print("========================================")

    # /ai-assistant/chat testi
    chat_data = {
        "messages": [
            {"role": "user", "content": "What is the capital of Uzbekistan?"}
        ]
    }
    test_endpoint("post", "/ai-assistant/chat", token, json_data=chat_data)

    # /ai-assistant/generate-text testi
    # Bu endpoint prompt'ni `data` (form data) sifatida qabul qiladi
    generate_text_data = {'prompt': 'Write a short story about an AI learning to dream.'}
    test_endpoint("post", "/ai-assistant/generate-text", token, data=generate_text_data)


def main():
    """Asosiy test funksiyasi."""
    token = get_access_token()
    if not token:
        return

    # --- Test qilinadigan funksiyalarni shu yerda chaqiring ---
    test_ai_assistant_endpoints(token)
    # Boshqa test funksiyalari (masalan, test_tts_endpoints) shu yerga qo'shiladi
    # ...

if __name__ == "__main__":
    main()
