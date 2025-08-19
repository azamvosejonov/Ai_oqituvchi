# O‘quv Platformasi API — Ishga tushirish va foydalanish qo‘llanmasi (UZ)

Bu fayl barcha asosiy API endpointlar nimani qiladi va ularni to‘liq ishlatish uchun nima qilish kerakligini qisqa va aniq tushuntiradi.

- Base URL: http://0.0.0.0:8004/api/v1
- Autentifikatsiya: Ko‘pchilik endpointlar JWT talab qiladi — `Authorization: Bearer <token>`
- Hujjatlar: Swagger UI — `GET /docs`, OpenAPI — `GET /api/v1/openapi.json`
- Statik va yuklamalar: `/static/*`, `/uploads/*`


## 1) Xizmatni 8004-portda ishga tushirish

Hozirgi konfiguratsiya 8002-portga yo‘naltirilgan (main.py, docker-compose, Dockerfile). 8004 uchun 2 oson yo‘l bor:

- Lokal (tavsiya):
  - `pip install -r requirements.txt`
  - `python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload`

- Docker (override bilan):
  - `docker compose build`
  - `docker compose run --service-ports --use-aliases api uvicorn main:app --host 0.0.0.0 --port 8004 --reload`
  - Yoki `docker-compose.yml` da `command` va `ports` ni 8004 ga moslab o‘zgartiring.

Eslatma: Test va probelar uchun BASE URL har doim `http://0.0.0.0:8004` bo‘lishi kerak.


## 2) Muhit sozlamalari (.env)

Minimal kerakli sozlamalar:
- `SECRET_KEY` — JWT uchun maxfiy kalit
- `DATABASE_URL` — DB ulanishi (agar Postgres bo‘lsa `postgresql+psycopg://...`)
- `REDIS_URL` — rate limiting va fon ishlar uchun (masalan, `redis://redis:6379/0`)
- `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD` — birlamchi admin yaratish
- `UPLOAD_DIR` — yuklamalar papkasi (default: `uploads`)
- AI:
  - `GOOGLE_API_KEY` — Gemini uchun talab qilinadi
  - Moslik uchun: `AI_API_KEY=<GOOGLE_API_KEY bilan bir xil qiymat>` — `app/api/api_v1/endpoints/ai.py` tekshiruvini qondiradi
- Test-optimizatsiya (ixtiyoriy):
  - `DISABLE_GEMINI=1` — tashqi LLM chaqiruvini o‘chiradi (test tezlashadi)
  - `DISABLE_WHISPER=1` — STT ni dummy qiladi
  - `DISABLE_TTS=1` — gTTS oqimini o‘chiradi (ba’zi holatlarda)


## 3) Autentifikatsiya va rollar

- Login: `POST /api/v1/login/access-token` (form: `username`, `password`)
- Token bilan so‘rov: `Authorization: Bearer <access_token>`
- Rollar: oddiy foydalanuvchi, premium, teacher, admin, superadmin
- Ko‘plab admin/teacher endpointlari faqat tegishli rol bilan ishlaydi


## 4) Rate limiting va kvotalar

- Rate limiting: slowapi (`@limiter.limit`) — misol: AI `ask` 30/min, TTS/STT 60/min, voice-loop 20/min
- Kvotalar (`crud_user_ai_usage`):
  - `gpt4o_requests_left` — AI matn so‘rovlar
  - `stt_requests_left` — STT chaqiruvlar
  - `tts_chars_left` — TTS belgilar limiti
  - `pronunciation_analysis_left` — talaffuz tahlillari


## 5) AI endpointlari (`/api/v1/ai`)

Fayl: `app/api/api_v1/endpoints/ai.py`, xizmatlar: `app/services/ai_service.py`

- GET `/ai/tts/voices` — gTTS tillari ro‘yxati (public)
- GET `/ai/stt/languages` — Whisper tillari ro‘yxati (public)
- POST `/ai/ask?speak=<bool>&language=<code>` — matnli savol, ixtiyoriy TTS (auth, 30/min)
  - Body: `{ "prompt": "Matn" }`
  - Javob: `{ text, avatar_type, avatar_name, audio_url? }`
- POST `/ai/tts` — matn → audio (MP3 stream) (auth, 60/min, `tts_chars_left` kamayadi)
  - Body: `{ "text": "...", "language": "uz" }`
  - Javob: `audio/mpeg`
- POST `/ai/stt` — audio → matn (auth, 60/min)
  - Form: `file=@audio.wav`
  - Javob: `{ "text": "..." }`
- POST `/ai/pronunciation` — talaffuzni baholash (auth)
  - Form: `file=@audio.wav`, `reference_text="..."`
  - Javob: `{ accuracy_score, transcribed_text, reference_text }`
- GET `/ai/pronunciation/history` — so‘nggi urinishlar (auth)
- GET `/ai/pronunciation/summary` — talaffuz profili (auth)
- GET `/ai/lessons/suggested?limit=5` — darajaga mos darslar (auth)
- POST `/ai/voice-loop` — gapiradi→tinglaydi→tahlil→TTS (auth, 20/min)
  - Form: `file=@audio.wav`, `language=uz`, `reference_text?`
  - Javob: `{ transcript, ai_text, corrections, advice, audio_url }`

Texnik:
- LLM: Google Gemini (`GOOGLE_API_KEY` shart). Test rejimida dummy javob bo‘lishi mumkin.
- TTS: gTTS — internet talab qilinadi.
- STT: Whisper “tiny” — CPU’da ishlaydi, og‘irroq bo‘lishi mumkin.


## 6) Talaffuz resurslari (`/api/v1/pronunciation`)

Fayl: `app/api/api_v1/endpoints/pronunciation.py`

- Phrases:
  - POST `/pronunciation/phrases/` — fraza yaratish (auth)
  - GET `/pronunciation/phrases/` — frazalar (auth, filter: level/skip/limit)
  - GET `/pronunciation/phrases/{id}` — fraza (auth)
  - PUT `/pronunciation/phrases/{id}` — yangilash (auth)
  - DELETE `/pronunciation/phrases/{id}` — o‘chirish (auth)
- Sessions:
  - POST `/pronunciation/sessions/` — sessiya yaratish (auth)
  - GET `/pronunciation/sessions/` — sessiyalar (auth)
  - GET `/pronunciation/sessions/{id}` — sessiya (auth)
  - PATCH `/pronunciation/sessions/{id}/complete` — yakunlash (auth)
- Analyze:
  - POST `/pronunciation/analyze/` — fraza bo‘yicha audio tahlil (auth)


## 7) Uyga vazifa (`/api/v1/homework`)

Fayl: `app/api/endpoints/homework.py`

- GET `/homework/` — foydalanuvchiga ko‘rinadigan homeworklar (auth)
- POST `/homework/` — homework yaratish (teacher/admin)
- GET `/homework/{homework_id}` — bitta homework (auth)
- GET `/homework/lesson/{lesson_id}` — dars bo‘yicha homeworklar (auth)
- GET `/homework/user/me` — joriy foydalanuvchi submissionlari (auth)
- GET `/homework/submissions/me` — soddalashtirilgan ro‘yxat (auth)
- POST `/homework/{homework_id}/submit` — matnli topshirish (auth)
- POST `/homework/{homework_id}/submit-oral` — audio topshirish (auth)
- POST `/homework/submissions/{submission_id}/grade` — baholash (teacher/admin)
- POST `/homework/grade/{submission_id}` — baholash (compat, JSON)
- POST `/homework/grade/{user_homework_id}` — baholash (compat, form)
- POST `/homework/{homework_id}/assign` — talabalar ro‘yxatiga biriktirish (teacher/admin)
- GET `/homework/files/{file_id}/download` — fayl yuklab olish (auth + ruxsat)

Texnik:
- Audio fayllar `uploads/homework/audio/` ga saqlanadi, public URL `/uploads/homework/audio/*`
- Audio topshirilganda fon ishlar: STT → auto-grade → feedback


## 8) Interaktiv darslar va boshqalar

Routerlar: `app/api/api_v1/api.py`

- Interactive lessons: `/interactive-lessons/` (ro‘yxat, detail), `/lesson-interactions/`, `/lesson-sessions/`
- Users: `/users/*` (me, list — admin), premium ma’lumotlar
- Courses, Lessons, Words: `/courses/`, `/lessons/`, `/words/`
- Subscriptions: `/subscriptions/plans`, `/subscriptions/me`, admin yo‘llari
- Payments: `/payments/` (tarix)
- Statistics: `/statistics/*`
- Notifications: `/notifications/*`
- Profile: `/profile/*`
- Content: `/content/lessons-json`, `/content/lessons`
- Forum: `/forum/*`
- Tests: `/tests/ielts`, `/tests/toefl`, `/tests/`
- Avatars: `/avatars/`
- Metrics: `/metrics`, `/metrics/health`, `/metrics/status`
- Recommendations: `/recommendations/*`
- Exercises: `/exercises/`


## 9) Tez start — cURL namunalar

- Login token olish:
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/login/access-token" \
 -H "Content-Type: application/x-www-form-urlencoded" \
 -d "username=admin@example.com&password=changethis"
```

- AI ask (TTS bilan):
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/ask?speak=true&language=uz" \
 -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
 -d '{"prompt":"Salom, menga yordam bering"}'
```

- TTS oqimi:
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/tts" \
 -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
 -d '{"text":"Assalomu alaykum!","language":"uz"}' -o out.mp3
```

- STT:
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/stt" \
 -H "Authorization: Bearer <TOKEN>" \
 -F "file=@tests/test_data/test_audio.wav"
```

- Talaffuz:
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/pronunciation" \
 -H "Authorization: Bearer <TOKEN>" \
 -F "file=@tests/test_data/test_audio.wav" \
 -F "reference_text=Hello this is a test"
```

- Voice loop:
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/voice-loop" \
 -H "Authorization: Bearer <TOKEN>" \
 -F "file=@tests/test_data/test_audio.wav" \
 -F "language=uz"
```

- Uyga vazifa yaratish (teacher/admin):
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/homework/" \
 -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
 -d '{"title":"Essay 1","description":"Write 150 words","course_id":1,"lesson_id":10}'
```

- Uyga vazifa og‘zaki topshirish:
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/homework/55/submit-oral" \
 -H "Authorization: Bearer <TOKEN>" \
 -F "audio_file=@tests/test_data/test_audio.wav"
```


## 10) Sog‘lomlik va versiya

- Health: `GET /health` → `{ "status": "ok" }`
- Version: `GET /version` → `{ "version": "1.0.0" }`


## 11) Smoke test (majburiy tavsiya)

- `LIVE_BASE_URL=http://0.0.0.0:8004 python scripts/live_smoke_test.py`
- Natijada barcha muhim endpointlar tekshiriladi. Maqsad: `OK=N, FAIL=0`.


## 12) Muammolarni yechish

- 503 “AI service is not configured”: `.env` ga `GOOGLE_API_KEY` qo‘shing va moslik uchun `AI_API_KEY` ni ham shunga teng qiling.
- 403 “quota exceeded”: foydalanuvchi kvotalarini oshirish yoki premium reja.
- 429 “Juda ko‘p so‘rov”: rate limiting sababli — kuting yoki limitni sozlang.
- TTS xatolari: gTTS internetga muhtoj — serverda chiqish borligini tekshiring.
- STT xatolari: Whisper modeli RAM/CPU talab qiladi — `DISABLE_WHISPER=1` bilan test rejimi.


## 13) Muhim fayllar va joylashuvlar

- Routerlar: `app/api/api_v1/api.py`
- AI endpointlar: `app/api/api_v1/endpoints/ai.py`
- AI servis: `app/services/ai_service.py`
- Uyga vazifa endpointlar: `app/api/endpoints/homework.py`
- Konfiguratsiya: `app/core/config.py`
- Asosiy app: `main.py`
- Docker compose: `docker-compose.yml`
- Smoke test: `scripts/live_smoke_test.py`
- Yuklamalar: `uploads/` (servis: `/uploads`)


## 14) 70 ta endpoint — to‘liq ro‘yxat va minimal parametrlar

Quyidagi ro‘yxat `scripts/live_smoke_test.py` dagi 70 ta endpointga mos keladi. Har birida:
- Auth: JWT talab qilinadimi
- Parametrlar: so‘rov turi va majburiy maydonlar
- Ishlashi uchun: minimal shart

1) POST `/api/v1/login/access-token`
- Auth: Yo‘q
- Parametrlar (form): `username`, `password`
- Ishlashi uchun: tizimda mavjud foydalanuvchi (masalan, `.env` dagi admin)

2) GET `/api/v1/login/test-token`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: to‘g‘ri Bearer token

3) POST `/api/v1/logout`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: faol token

4) GET `/api/v1/users/me`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: faol token

5) GET `/api/v1/users/me/premium-data`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: premium bo‘lsa to‘liq; oddiyda cheklangan ma’lumot

6) GET `/api/v1/users/me/next-lesson`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: tizimda darslar mavjud bo‘lishi kerak

7) GET `/api/v1/users/test-superuser`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: superuser bo‘lsa 200, aks holda 403

8) GET `/api/v1/users/`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin/superuser roli

9) GET `/api/v1/users/certificates/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchining sertifikatlari bo‘lishi mumkin

10) GET `/api/v1/subscription-plans/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: ma’lumotlar mavjud

11) GET `/api/v1/subscriptions/plans`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: ma’lumotlar mavjud

12) GET `/api/v1/subscriptions/status`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchining obuna holati mavjud

13) GET `/api/v1/subscriptions/`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin ruxsati

14) GET `/api/v1/subscriptions/me`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi obunasi bo‘lishi mumkin

15) GET `/api/v1/subscriptions/admin/config-check`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin ruxsati

16) GET `/api/v1/courses/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: kurslar mavjud

17) GET `/api/v1/lessons/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: darslar mavjud

18) GET `/api/v1/lessons/categories`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: kategoriyalar mavjud

19) GET `/api/v1/lessons/videos`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: videolar mavjud

20) GET `/api/v1/lessons/continue`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi uchun davom etilayotgan dars bo‘lishi mumkin

21) GET `/api/v1/words/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: so‘zlar mavjud

22) GET `/api/v1/statistics/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: statistik ma’lumotlar generatsiyasi yoqilgan

23) GET `/api/v1/statistics/top-users`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi ballari mavjud

24) GET `/api/v1/statistics/payment-stats`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: to‘lovlar bo‘yicha ma’lumotlar mavjud

25) GET `/api/v1/user-progress/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi faoliyati mavjud

26) GET `/api/v1/user-progress/last`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: so‘nggi faoliyat mavjud

27) GET `/api/v1/certificates/my-certificates`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: sertifikatlar mavjud bo‘lishi mumkin

28) GET `/api/v1/feedback/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi fikrlari bo‘lishi mumkin

29) GET `/api/v1/forum/categories/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: forum kategoriyalari mavjud

30) GET `/api/v1/forum/topics/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: forum mavzulari mavjud

31) GET `/api/v1/ai/tts/voices`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: gTTS tillar ro‘yxati qaytadi

32) GET `/api/v1/ai/stt/languages`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: Whisper tillar ro‘yxati qaytadi

33) POST `/api/v1/ai/analyze-answer`
- Auth: Yo‘q
- Parametrlar (JSON): `user_response` (majburiy), `reference_text` (ixtiyoriy), `language` (ixtiyoriy)
- Ishlashi uchun: `user_response` matni berilishi shart

34) GET `/api/v1/ai/usage`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi kvota yozuvi mavjud

35) GET `/api/v1/ai-sessions/sessions`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: AI sessiyalar mavjud bo‘lishi mumkin

36) GET `/api/v1/notifications/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: bildirishnomalar bo‘lishi mumkin

37) GET `/api/v1/notifications/unread-count`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: o‘qilmaganlar soni qaytadi

38) GET `/api/v1/tests/ielts`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: IELTS test ma’lumotlari mavjud

39) GET `/api/v1/tests/toefl`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: TOEFL test ma’lumotlari mavjud

40) GET `/api/v1/tests/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: umumiy testlar ro‘yxati

41) GET `/api/v1/admin/statistics`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin ruxsati

42) GET `/api/v1/admin/users`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin ruxsati

43) GET `/api/v1/admin/subscription-plans/`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin ruxsati

44) GET `/api/v1/admin/courses/`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin ruxsati

45) GET `/api/v1/admin/interactive-lessons/`
- Auth: Ha (admin)
- Parametrlar: Yo‘q
- Ishlashi uchun: admin ruxsati

46) GET `/api/v1/content/lessons/validate`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: kontent validatsiyasi yoqilgan

47) GET `/api/v1/content/lessons-json`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: darslar JSON fayli mavjud

48) GET `/api/v1/content/lessons`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: dars kontenti mavjud

49) GET `/api/v1/content/media`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: media ro‘yxati mavjud

50) GET `/api/v1/profile/me`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: profil ma’lumoti mavjud

51) GET `/api/v1/profile/stats`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi statistikasi mavjud

52) GET `/api/v1/pronunciation/phrases/`
- Auth: Ha
- Parametrlar (query ixtiyoriy): `level`, `skip`, `limit`
- Ishlashi uchun: frazalar mavjud

53) GET `/api/v1/pronunciation/sessions/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: talaffuz sessiyalari bo‘lishi mumkin

54) GET `/api/v1/pronunciation/history/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi talaffuz tarixi bo‘lishi mumkin

55) GET `/api/v1/pronunciation/profile/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: profil xulosasi qaytadi

56) GET `/api/v1/interactive-lessons/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: interaktiv darslar ro‘yxati mavjud

57) GET `/api/v1/interactive-lessons/1`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: ID=1 mavjud bo‘lmasa, ro‘yxatdan haqiqiy ID bilan qayta urinib ko‘ring

58) GET `/api/v1/lesson-sessions/user/me`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: dars sessiyalari mavjud bo‘lishi mumkin

59) GET `/api/v1/homework/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchiga tegishli homeworklar mavjud

60) GET `/api/v1/homework/user/me`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi submissionlari bo‘lishi mumkin

61) GET `/api/v1/homework/submissions/me`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: soddalashtirilgan submissionlar ro‘yxati

62) GET `/api/v1/payments/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi to‘lov tarixi

63) GET `/api/v1/avatars/`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: avatarlar ro‘yxati

64) GET `/api/v1/metrics`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: tizim metrikalari

65) GET `/api/v1/metrics/health`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: `{ "status": "ok" }`

66) GET `/api/v1/metrics/status`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: xizmatlar holati

67) GET `/api/v1/recommendations/next-lessons`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi uchun tavsiya darslar

68) GET `/api/v1/recommendations/personalized`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: shaxsiy tavsiyalar

69) GET `/api/v1/recommendations/for-you`
- Auth: Ha
- Parametrlar: Yo‘q
- Ishlashi uchun: foydalanuvchi uchun tavsiyalar

70) GET `/api/v1/exercises/`
- Auth: Yo‘q
- Parametrlar: Yo‘q
- Ishlashi uchun: mashqlar ro‘yxati


---

Agar xohlasangiz, 8004 ga to‘liq migratsiya (compose/Dockerfile/main.py patchlari) va LIVE smoke testni men bajarib, natijani taqdim etaman.
