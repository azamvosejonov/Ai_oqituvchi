# O‘quv Platformasi API Qo‘llanma

- Base URL: http://0.0.0.0:8004/api/v1
- Har bir endpoint bir xil formatda ko‘rsatilgan: Endpoint → Parametrlar → So‘rov → Majburiy maydonlar → Javob → cURL
- Auth soddalashtirilgan ko‘rinishda berilgan (Admin/Superuser yoki JWT yoki Public)

## admin
- __[Endpoint]__ GET /api/v1/admin/courses/
- __[Tavsif]__ Barcha kurslarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "description": "string",
    "difficulty_level": "string",
    "short_description": "string",
    "thumbnail_url": "string",
    "is_published": true,
    "is_featured": true,
    "estimated_duration": 0,
    "language": "string",
    "price": 0,
    "discount_price": 0,
    "category": "string",
    "tags": [
      "string"
    ],
    "requirements": [
      "string"
    ],
    "learning_outcomes": [
      "string"
    ],
    "id": 0,
    "instructor_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lessons": []
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/admin/courses/"
```



- __[Endpoint]__ POST /api/v1/admin/courses/
- __[Tavsif]__ Yangi kurs yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "instructor_id": 0
}
```

- __[Majburiy maydonlar]__ `title`, `difficulty_level`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "id": 0,
  "instructor_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lessons": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/admin/courses/" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "difficulty_level": "string", "short_description": "string", "thumbnail_url": "string", "is_published": true, "is_featured": true, "estimated_duration": 0, "language": "string", "price": 0, "discount_price": 0, "category": "string", "tags": ["string"], "requirements": ["string"], "learning_outcomes": ["string"], "instructor_id": 0}'
```



- __[Endpoint]__ DELETE /api/v1/admin/courses/{course_id}
- __[Tavsif]__ kursni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `course_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `course_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "id": 0,
  "instructor_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lessons": []
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/admin/courses/{course_id}"
```



- __[Endpoint]__ PUT /api/v1/admin/courses/{course_id}
- __[Tavsif]__ kursni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `course_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ]
}
```

- __[Majburiy maydonlar]__ `course_id`, `title`, `difficulty_level`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "id": 0,
  "instructor_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lessons": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/admin/courses/{course_id}" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "difficulty_level": "string", "short_description": "string", "thumbnail_url": "string", "is_published": true, "is_featured": true, "estimated_duration": 0, "language": "string", "price": 0, "discount_price": 0, "category": "string", "tags": ["string"], "requirements": ["string"], "learning_outcomes": ["string"]}'
```



- __[Endpoint]__ GET /api/v1/admin/interactive-lessons/
- __[Tavsif]__ Barcha interaktiv darslarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "order": 0,
    "description": "string",
    "video_url": "string",
    "difficulty": "beginner",
    "is_premium": false,
    "is_active": true,
    "content": {},
    "tags": [
      "string"
    ],
    "estimated_duration": 0,
    "id": 0,
    "course_id": 0,
    "avatar_id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/admin/interactive-lessons/"
```



- __[Endpoint]__ POST /api/v1/admin/interactive-lessons/
- __[Tavsif]__ Yangi interaktiv dars yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "order": 0,
  "description": "string",
  "video_url": "string",
  "difficulty": "beginner",
  "is_premium": false,
  "is_active": true,
  "content": {},
  "tags": [
    "string"
  ],
  "estimated_duration": 0,
  "course_id": 0,
  "avatar_id": 0
}
```

- __[Majburiy maydonlar]__ `title`, `order`, `avatar_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "order": 0,
  "description": "string",
  "video_url": "string",
  "difficulty": "beginner",
  "is_premium": false,
  "is_active": true,
  "content": {},
  "tags": [
    "string"
  ],
  "estimated_duration": 0,
  "id": 0,
  "course_id": 0,
  "avatar_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/admin/interactive-lessons/" \
 -H 'Content-Type: application/json' -d '{"title": "string", "order": 0, "description": "string", "video_url": "string", "difficulty": "beginner", "is_premium": false, "is_active": true, "content": {}, "tags": ["string"], "estimated_duration": 0, "course_id": 0, "avatar_id": 0}'
```



- __[Endpoint]__ DELETE /api/v1/admin/interactive-lessons/{lesson_id}
- __[Tavsif]__ interaktiv darsni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `lesson_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `lesson_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "order": 0,
  "description": "string",
  "video_url": "string",
  "difficulty": "beginner",
  "is_premium": false,
  "is_active": true,
  "content": {},
  "tags": [
    "string"
  ],
  "estimated_duration": 0,
  "id": 0,
  "course_id": 0,
  "avatar_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/admin/interactive-lessons/{lesson_id}"
```



- __[Endpoint]__ PUT /api/v1/admin/interactive-lessons/{lesson_id}
- __[Tavsif]__ interaktiv darsni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `lesson_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "order": 0,
  "description": "string",
  "video_url": "string",
  "difficulty": "beginner",
  "is_premium": false,
  "is_active": true,
  "content": {},
  "tags": [
    "string"
  ],
  "estimated_duration": 0
}
```

- __[Majburiy maydonlar]__ `lesson_id`, `title`, `order`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "order": 0,
  "description": "string",
  "video_url": "string",
  "difficulty": "beginner",
  "is_premium": false,
  "is_active": true,
  "content": {},
  "tags": [
    "string"
  ],
  "estimated_duration": 0,
  "id": 0,
  "course_id": 0,
  "avatar_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/admin/interactive-lessons/{lesson_id}" \
 -H 'Content-Type: application/json' -d '{"title": "string", "order": 0, "description": "string", "video_url": "string", "difficulty": "beginner", "is_premium": false, "is_active": true, "content": {}, "tags": ["string"], "estimated_duration": 0}'
```



- __[Endpoint]__ GET /api/v1/admin/statistics
- __[Tavsif]__ olish admin dashboard statistics.
- Total users
- Premium users
- Active subscriptions
- Total revenue
- etc.
Faqat superuserlar uchun.
- __[Auth]__ Ha (Admin/Superuser)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "total_users": 0,
  "premium_users": 0,
  "total_courses": 0,
  "total_lessons": 0,
  "total_words": 0,
  "active_subscriptions": 0,
  "total_revenue": 0,
  "ai_usage_stats": {
    "gpt4o_requests": 0,
    "stt_requests": 0,
    "tts_characters": 0,
    "pronunciation_analysis": 0
  },
  "pending_payments": 0,
  "top_learners": [
    {
      "full_name": "string",
      "completed_lessons": 0
    }
  ],
  "top_courses": [
    {
      "title": "string",
      "enrolled_users": 0
    }
  ]
}
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/admin/statistics"
```



- __[Endpoint]__ GET /api/v1/admin/subscription-plans/
- __[Tavsif]__ Barcha obuna rejalarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "name": "string",
    "price": 0,
    "duration_days": 0,
    "description": "string",
    "stripe_price_id": "string",
    "gpt4o_requests_quota": 0,
    "stt_requests_quota": 0,
    "tts_chars_quota": 0,
    "pronunciation_analysis_quota": 0,
    "id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/admin/subscription-plans/"
```



- __[Endpoint]__ POST /api/v1/admin/subscription-plans/
- __[Tavsif]__ Yangi obuna reja yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0
}
```

- __[Majburiy maydonlar]__ `name`, `price`, `duration_days`, `stripe_price_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0,
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/admin/subscription-plans/" \
 -H 'Content-Type: application/json' -d '{"name": "string", "price": 0, "duration_days": 0, "description": "string", "stripe_price_id": "string", "gpt4o_requests_quota": 0, "stt_requests_quota": 0, "tts_chars_quota": 0, "pronunciation_analysis_quota": 0}'
```



- __[Endpoint]__ DELETE /api/v1/admin/subscription-plans/{plan_id}
- __[Tavsif]__ obuna rejani o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `plan_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `plan_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0,
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/admin/subscription-plans/{plan_id}"
```



- __[Endpoint]__ PUT /api/v1/admin/subscription-plans/{plan_id}
- __[Tavsif]__ obuna rejani yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `plan_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0
}
```

- __[Majburiy maydonlar]__ `plan_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0,
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/admin/subscription-plans/{plan_id}" \
 -H 'Content-Type: application/json' -d '{"name": "string", "price": 0, "duration_days": 0, "description": "string", "stripe_price_id": "string", "gpt4o_requests_quota": 0, "stt_requests_quota": 0, "tts_chars_quota": 0, "pronunciation_analysis_quota": 0}'
```



- __[Endpoint]__ GET /api/v1/admin/users
- __[Tavsif]__ Barcha foydalanuvchilarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
  - query: `role` (string) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/admin/users"
```



- __[Endpoint]__ POST /api/v1/admin/users
- __[Tavsif]__ Yangi foydalanuvchi yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "username": "string",
  "password": "string"
}
```

- __[Majburiy maydonlar]__ `email`, `username`, `password`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/admin/users" \
 -H 'Content-Type: application/json' -d '{"email": "string", "is_active": true, "is_superuser": false, "full_name": "string", "current_level": "string", "last_viewed_lesson_id": 0, "username": "string", "password": "string"}'
```



- __[Endpoint]__ DELETE /api/v1/admin/users/{user_id}
- __[Tavsif]__ foydalanuvchini o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
{
  "msg": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/admin/users/{user_id}"
```



- __[Endpoint]__ GET /api/v1/admin/users/{user_id}
- __[Tavsif]__ olish a specific user by id. Faqat adminlar uchun.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/admin/users/{user_id}"
```



- __[Endpoint]__ PATCH /api/v1/admin/users/{user_id}
- __[Tavsif]__ foydalanuvchini yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "role": "free"
}
```

- __[Majburiy maydonlar]__ `user_id`, `role`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -X PATCH "http://0.0.0.0:8004/api/v1/admin/users/{user_id}" \
 -H 'Content-Type: application/json' -d '{"role": "free"}'
```



- __[Endpoint]__ PATCH /api/v1/admin/users/{user_id}/profile
- __[Tavsif]__ profilni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "full_name": "string",
  "email": "string"
}
```

- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -X PATCH "http://0.0.0.0:8004/api/v1/admin/users/{user_id}/profile" \
 -H 'Content-Type: application/json' -d '{"full_name": "string", "email": "string"}'
```



- __[Endpoint]__ PATCH /api/v1/admin/users/{user_id}/role
- __[Tavsif]__ roleni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "role": "free"
}
```

- __[Majburiy maydonlar]__ `user_id`, `role`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -X PATCH "http://0.0.0.0:8004/api/v1/admin/users/{user_id}/role" \
 -H 'Content-Type: application/json' -d '{"role": "free"}'
```



## admin-tests
- __[Endpoint]__ POST /api/v1/admin/tests/
- __[Tavsif]__ Yangi test yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "test_type": "ielts",
  "duration_minutes": 0,
  "is_active": true
}
```

- __[Majburiy maydonlar]__ `title`, `test_type`, `duration_minutes`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "test_type": "ielts",
  "duration_minutes": 0,
  "is_active": true,
  "id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "sections": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/admin/tests/" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "test_type": "ielts", "duration_minutes": 0, "is_active": true}'
```



- __[Endpoint]__ DELETE /api/v1/admin/tests/questions/{question_id}
- __[Tavsif]__ questionsni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `question_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `question_id`
- __[Javob namunasi]__
```json
string
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/admin/tests/questions/{question_id}"
```



- __[Endpoint]__ PUT /api/v1/admin/tests/questions/{question_id}
- __[Tavsif]__ questionsni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `question_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "question_text": "string",
  "question_data": {},
  "marks": 0,
  "order_index": 0
}
```

- __[Majburiy maydonlar]__ `question_id`
- __[Javob namunasi]__
```json
{
  "question_type": "multiple_choice",
  "question_text": "string",
  "question_data": {},
  "marks": 1.0,
  "order_index": 0,
  "id": 0,
  "section_id": 0,
  "answers": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/admin/tests/questions/{question_id}" \
 -H 'Content-Type: application/json' -d '{"question_text": "string", "question_data": {}, "marks": 0, "order_index": 0}'
```



- __[Endpoint]__ DELETE /api/v1/admin/tests/sections/{section_id}
- __[Tavsif]__ sectionsni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `section_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `section_id`
- __[Javob namunasi]__
```json
string
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/admin/tests/sections/{section_id}"
```



- __[Endpoint]__ PUT /api/v1/admin/tests/sections/{section_id}
- __[Tavsif]__ sectionsni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `section_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "instructions": "string",
  "duration_minutes": 0,
  "order_index": 0
}
```

- __[Majburiy maydonlar]__ `section_id`
- __[Javob namunasi]__
```json
{
  "section_type": "listening",
  "title": "string",
  "description": "string",
  "instructions": "string",
  "duration_minutes": 0,
  "order_index": 0,
  "id": 0,
  "test_id": 0,
  "questions": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/admin/tests/sections/{section_id}" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "instructions": "string", "duration_minutes": 0, "order_index": 0}'
```



- __[Endpoint]__ POST /api/v1/admin/tests/sections/{section_id}/questions/
- __[Tavsif]__ Yangi questions yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `section_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "question_type": "multiple_choice",
  "question_text": "string",
  "question_data": {},
  "marks": 1.0,
  "order_index": 0,
  "section_id": 0
}
```

- __[Majburiy maydonlar]__ `section_id`, `question_type`, `question_text`, `question_data`
- __[Javob namunasi]__
```json
{
  "question_type": "multiple_choice",
  "question_text": "string",
  "question_data": {},
  "marks": 1.0,
  "order_index": 0,
  "id": 0,
  "section_id": 0,
  "answers": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/admin/tests/sections/{section_id}/questions/" \
 -H 'Content-Type: application/json' -d '{"question_type": "multiple_choice", "question_text": "string", "question_data": {}, "marks": 1.0, "order_index": 0, "section_id": 0}'
```



- __[Endpoint]__ PUT /api/v1/admin/tests/{test_id}
- __[Tavsif]__ testni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `test_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "test_type": "ielts",
  "duration_minutes": 0,
  "is_active": true
}
```

- __[Majburiy maydonlar]__ `test_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "test_type": "ielts",
  "duration_minutes": 0,
  "is_active": true,
  "id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "sections": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/admin/tests/{test_id}" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "test_type": "ielts", "duration_minutes": 0, "is_active": true}'
```



- __[Endpoint]__ POST /api/v1/admin/tests/{test_id}/sections/
- __[Tavsif]__ Yangi sections yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `test_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "section_type": "listening",
  "title": "string",
  "description": "string",
  "instructions": "string",
  "duration_minutes": 0,
  "order_index": 0,
  "test_id": 0
}
```

- __[Majburiy maydonlar]__ `test_id`, `section_type`, `title`, `duration_minutes`
- __[Javob namunasi]__
```json
{
  "section_type": "listening",
  "title": "string",
  "description": "string",
  "instructions": "string",
  "duration_minutes": 0,
  "order_index": 0,
  "id": 0,
  "test_id": 0,
  "questions": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/admin/tests/{test_id}/sections/" \
 -H 'Content-Type: application/json' -d '{"section_type": "listening", "title": "string", "description": "string", "instructions": "string", "duration_minutes": 0, "order_index": 0, "test_id": 0}'
```



## ai
- __[Endpoint]__ POST /api/v1/ai/ask
- __[Tavsif]__ Receives a text prompt and returns a text-based answer from the AI.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "prompt": "string"
}
```

- __[Majburiy maydonlar]__ `prompt`
- __[Javob namunasi]__
```json
{
  "text": "string",
  "audio_url": "string",
  "avatar_type": "string",
  "avatar_name": "string",
  "suggestions": [
    "string"
  ]
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/ask" \
 -H 'Content-Type: application/json' -d '{"prompt": "string"}'
```



- __[Endpoint]__ POST /api/v1/ai/pronunciation
- __[Tavsif]__ Assesses the pronunciation of an audio file against a reference text using a free, local model.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Form-Data
```json
{
  "file": "(binary file)",
  "reference_text": "string"
}
```

- __[Majburiy maydonlar]__ `file`, `reference_text`
- __[Javob namunasi]__
```json
{
  "accuracy_score": 0,
  "reference_text": "string",
  "transcribed_text": "string",
  "error": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/pronunciation"  \
 -F "file=(binary file)"
 -F "reference_text=string"
```



- __[Endpoint]__ POST /api/v1/ai/stt
- __[Tavsif]__ Transcribes audio to text using the Whisper model.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Form-Data
```json
{
  "file": "(binary file)"
}
```

- __[Majburiy maydonlar]__ `file`
- __[Javob namunasi]__
```json
{
  "text": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/stt"  \
 -F "file=(binary file)"
```



- __[Endpoint]__ POST /api/v1/ai/suggest-lesson
- __[Tavsif]__ Suggests a new lesson for the user based on their progress.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "title": "string",
  "order": 0,
  "description": "string",
  "video_url": "string",
  "difficulty": "beginner",
  "is_premium": false,
  "is_active": true,
  "content": {},
  "tags": [
    "string"
  ],
  "estimated_duration": 0,
  "id": 0,
  "course_id": 0,
  "avatar_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/suggest-lesson"
```



- __[Endpoint]__ POST /api/v1/ai/tts
- __[Tavsif]__ Converts text to speech and streams the audio back.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "text": "string",
  "language": "en-US"
}
```

- __[Majburiy maydonlar]__ `text`
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai/tts" \
 -H 'Content-Type: application/json' -d '{"text": "string", "language": "en-US"}'
```



## avatars
- __[Endpoint]__ GET /api/v1/avatars/
- __[Tavsif]__ olish available AI avatars with their configurations.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {}
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/avatars/"
```



- __[Endpoint]__ GET /api/v1/avatars/{avatar_id}
- __[Tavsif]__ olish configuration for a specific avatar.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `avatar_id` (string) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `avatar_id`
- __[Javob namunasi]__
```json
{}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/avatars/{avatar_id}"
```



## certificates
- __[Endpoint]__ POST /api/v1/certificates/
- __[Tavsif]__ Yangi sertifikat yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "user_id": 0,
  "course_id": 0,
  "course_name": "string",
  "level_completed": "string",
  "description": "string",
  "verification_code": "string"
}
```

- __[Majburiy maydonlar]__ `title`, `user_id`, `course_name`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "user_id": 0,
  "course_id": 0,
  "course_name": "string",
  "level_completed": "string",
  "description": "string",
  "verification_code": "string",
  "id": 0,
  "issue_date": "2025-01-01T00:00:00Z",
  "is_valid": true,
  "file_path": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/certificates/" \
 -H 'Content-Type: application/json' -d '{"title": "string", "user_id": 0, "course_id": 0, "course_name": "string", "level_completed": "string", "description": "string", "verification_code": "string"}'
```



- __[Endpoint]__ GET /api/v1/certificates/my-certificates
- __[Tavsif]__ my certificatesni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "user_id": 0,
    "course_id": 0,
    "course_name": "string",
    "level_completed": "string",
    "description": "string",
    "verification_code": "string",
    "id": 0,
    "issue_date": "2025-01-01T00:00:00Z",
    "is_valid": true,
    "file_path": "string"
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/certificates/my-certificates"
```



- __[Endpoint]__ GET /api/v1/certificates/user/{user_id}
- __[Tavsif]__ foydalanuvchini olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "user_id": 0,
    "course_id": 0,
    "course_name": "string",
    "level_completed": "string",
    "description": "string",
    "verification_code": "string",
    "id": 0,
    "issue_date": "2025-01-01T00:00:00Z",
    "is_valid": true,
    "file_path": "string"
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/certificates/user/{user_id}"
```



- __[Endpoint]__ GET /api/v1/certificates/{certificate_id}/download
- __[Tavsif]__ Download a certificate as a PDF file.
Only the owner or an admin can download it.
- __[Auth]__ Ha (JWT, egalik tekshiruvi)
- __[Parametrlar]__
  - path: `certificate_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `certificate_id`
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/certificates/{certificate_id}/download"
```



- __[Endpoint]__ GET /api/v1/certificates/{certificate_id}/verify/{verification_code}
- __[Tavsif]__ Verify a certificate by its verification code.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `certificate_id` (integer) — Majburiy
  - path: `verification_code` (string) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `certificate_id`, `verification_code`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "user_id": 0,
  "course_id": 0,
  "course_name": "string",
  "level_completed": "string",
  "description": "string",
  "verification_code": "string",
  "id": 0,
  "issue_date": "2025-01-01T00:00:00Z",
  "is_valid": true,
  "file_path": "string"
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/certificates/{certificate_id}/verify/{verification_code}"
```



## courses
- __[Endpoint]__ GET /api/v1/courses/
- __[Tavsif]__ kurslarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "description": "string",
    "difficulty_level": "string",
    "short_description": "string",
    "thumbnail_url": "string",
    "is_published": true,
    "is_featured": true,
    "estimated_duration": 0,
    "language": "string",
    "price": 0,
    "discount_price": 0,
    "category": "string",
    "tags": [
      "string"
    ],
    "requirements": [
      "string"
    ],
    "learning_outcomes": [
      "string"
    ],
    "id": 0,
    "instructor_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lessons": []
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/courses/"
```



- __[Endpoint]__ POST /api/v1/courses/
- __[Tavsif]__ Yangi kurs yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "instructor_id": 0
}
```

- __[Majburiy maydonlar]__ `title`, `difficulty_level`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "id": 0,
  "instructor_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lessons": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/courses/" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "difficulty_level": "string", "short_description": "string", "thumbnail_url": "string", "is_published": true, "is_featured": true, "estimated_duration": 0, "language": "string", "price": 0, "discount_price": 0, "category": "string", "tags": ["string"], "requirements": ["string"], "learning_outcomes": ["string"], "instructor_id": 0}'
```



- __[Endpoint]__ DELETE /api/v1/courses/{id}
- __[Tavsif]__ kursni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "id": 0,
  "instructor_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lessons": []
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/courses/{id}"
```



- __[Endpoint]__ GET /api/v1/courses/{id}
- __[Tavsif]__ kursni ID bo‘yicha olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "id": 0,
  "instructor_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lessons": []
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/courses/{id}"
```



- __[Endpoint]__ PUT /api/v1/courses/{id}
- __[Tavsif]__ kursni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ]
}
```

- __[Majburiy maydonlar]__ `id`, `title`, `difficulty_level`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "string",
  "short_description": "string",
  "thumbnail_url": "string",
  "is_published": true,
  "is_featured": true,
  "estimated_duration": 0,
  "language": "string",
  "price": 0,
  "discount_price": 0,
  "category": "string",
  "tags": [
    "string"
  ],
  "requirements": [
    "string"
  ],
  "learning_outcomes": [
    "string"
  ],
  "id": 0,
  "instructor_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lessons": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/courses/{id}" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "difficulty_level": "string", "short_description": "string", "thumbnail_url": "string", "is_published": true, "is_featured": true, "estimated_duration": 0, "language": "string", "price": 0, "discount_price": 0, "category": "string", "tags": ["string"], "requirements": ["string"], "learning_outcomes": ["string"]}'
```



## feedback
- __[Endpoint]__ GET /api/v1/feedback/
- __[Tavsif]__ olish feedback.
- Regular users can see their own feedback.
- Admins can see all feedback.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "content": "string",
    "rating": 0,
    "id": 0,
    "user_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/feedback/"
```



- __[Endpoint]__ POST /api/v1/feedback/
- __[Tavsif]__ Yangi fikr-mulohaza yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "content": "string",
  "rating": 0
}
```

- __[Majburiy maydonlar]__ `content`
- __[Javob namunasi]__
```json
{
  "content": "string",
  "rating": 0,
  "id": 0,
  "user_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/feedback/" \
 -H 'Content-Type: application/json' -d '{"content": "string", "rating": 0}'
```



- __[Endpoint]__ DELETE /api/v1/feedback/{id}
- __[Tavsif]__ fikr-mulohazani o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "content": "string",
  "rating": 0,
  "id": 0,
  "user_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/feedback/{id}"
```



## forum
- __[Endpoint]__ GET /api/v1/forum/categories/
- __[Tavsif]__ Barcha categoriesni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "name": "string",
    "description": "string",
    "id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/forum/categories/"
```



- __[Endpoint]__ POST /api/v1/forum/categories/
- __[Tavsif]__ Yangi categories yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "name": "string",
  "description": "string"
}
```

- __[Majburiy maydonlar]__ `name`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "description": "string",
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/forum/categories/" \
 -H 'Content-Type: application/json' -d '{"name": "string", "description": "string"}'
```



- __[Endpoint]__ DELETE /api/v1/forum/categories/{category_id}
- __[Tavsif]__ categoriesni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `category_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `category_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "description": "string",
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/forum/categories/{category_id}"
```



- __[Endpoint]__ PUT /api/v1/forum/categories/{category_id}
- __[Tavsif]__ categoriesni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `category_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "name": "string",
  "description": "string"
}
```

- __[Majburiy maydonlar]__ `category_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "description": "string",
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/forum/categories/{category_id}" \
 -H 'Content-Type: application/json' -d '{"name": "string", "description": "string"}'
```



- __[Endpoint]__ GET /api/v1/forum/categories/{category_id}/topics
- __[Tavsif]__ Barcha mavzularni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `category_id` (integer) — Majburiy
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `category_id`
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "description": "string",
    "id": 0,
    "author_id": 0,
    "category_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "is_pinned": true,
    "is_closed": true,
    "author": {
      "email": "string",
      "is_active": true,
      "is_superuser": false,
      "full_name": "string",
      "current_level": "string",
      "last_viewed_lesson_id": 0,
      "id": 0,
      "roles": [],
      "is_premium": true,
      "role": "free"
    },
    "category": {
      "name": "string",
      "description": "string",
      "id": 0
    },
    "posts": []
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/forum/categories/{category_id}/topics"
```



- __[Endpoint]__ POST /api/v1/forum/posts/
- __[Tavsif]__ Yangi post yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "content": "string",
  "topic_id": 0,
  "parent_id": 0
}
```

- __[Majburiy maydonlar]__ `content`, `topic_id`
- __[Javob namunasi]__
```json
{
  "content": "string",
  "id": 0,
  "topic_id": 0,
  "author_id": 0,
  "parent_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "is_edited": true,
  "author": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "replies": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/forum/posts/" \
 -H 'Content-Type: application/json' -d '{"content": "string", "topic_id": 0, "parent_id": 0}'
```



- __[Endpoint]__ DELETE /api/v1/forum/posts/{post_id}
- __[Tavsif]__ postni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `post_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `post_id`
- __[Javob namunasi]__
```json
{
  "content": "string",
  "id": 0,
  "topic_id": 0,
  "author_id": 0,
  "parent_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "is_edited": true,
  "author": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "replies": []
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/forum/posts/{post_id}"
```



- __[Endpoint]__ PUT /api/v1/forum/posts/{post_id}
- __[Tavsif]__ postni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `post_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "content": "string"
}
```

- __[Majburiy maydonlar]__ `post_id`
- __[Javob namunasi]__
```json
{
  "content": "string",
  "id": 0,
  "topic_id": 0,
  "author_id": 0,
  "parent_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "is_edited": true,
  "author": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "replies": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/forum/posts/{post_id}" \
 -H 'Content-Type: application/json' -d '{"content": "string"}'
```



- __[Endpoint]__ GET /api/v1/forum/topics/
- __[Tavsif]__ Barcha mavzularni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "description": "string",
    "id": 0,
    "author_id": 0,
    "category_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "is_pinned": true,
    "is_closed": true,
    "author": {
      "email": "string",
      "is_active": true,
      "is_superuser": false,
      "full_name": "string",
      "current_level": "string",
      "last_viewed_lesson_id": 0,
      "id": 0,
      "roles": [],
      "is_premium": true,
      "role": "free"
    },
    "category": {
      "name": "string",
      "description": "string",
      "id": 0
    },
    "posts": []
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/forum/topics/"
```



- __[Endpoint]__ POST /api/v1/forum/topics/
- __[Tavsif]__ Yangi mavzu yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "category_id": 0,
  "content": "string"
}
```

- __[Majburiy maydonlar]__ `title`, `category_id`, `content`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "id": 0,
  "author_id": 0,
  "category_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "is_pinned": true,
  "is_closed": true,
  "author": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "category": {
    "name": "string",
    "description": "string",
    "id": 0
  },
  "posts": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/forum/topics/" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "category_id": 0, "content": "string"}'
```



- __[Endpoint]__ DELETE /api/v1/forum/topics/{topic_id}
- __[Tavsif]__ mavzuni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `topic_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `topic_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "id": 0,
  "author_id": 0,
  "category_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "is_pinned": true,
  "is_closed": true,
  "author": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "category": {
    "name": "string",
    "description": "string",
    "id": 0
  },
  "posts": []
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/forum/topics/{topic_id}"
```



- __[Endpoint]__ GET /api/v1/forum/topics/{topic_id}
- __[Tavsif]__ mavzularni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `topic_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `topic_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "id": 0,
  "author_id": 0,
  "category_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "is_pinned": true,
  "is_closed": true,
  "author": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "category": {
    "name": "string",
    "description": "string",
    "id": 0
  },
  "posts": []
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/forum/topics/{topic_id}"
```



- __[Endpoint]__ PUT /api/v1/forum/topics/{topic_id}
- __[Tavsif]__ mavzuni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `topic_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "description": "string",
  "is_pinned": true,
  "is_closed": true,
  "category_id": 0
}
```

- __[Majburiy maydonlar]__ `topic_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "id": 0,
  "author_id": 0,
  "category_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "is_pinned": true,
  "is_closed": true,
  "author": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "category": {
    "name": "string",
    "description": "string",
    "id": 0
  },
  "posts": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/forum/topics/{topic_id}" \
 -H 'Content-Type: application/json' -d '{"title": "string", "description": "string", "is_pinned": true, "is_closed": true, "category_id": 0}'
```



## health
- __[Endpoint]__ GET /health
- __[Tavsif]__ Health Check
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/health"
```



## homework
- __[Endpoint]__ GET /api/v1/homework/
- __[Tavsif]__ olish list of homework assignments available to the user.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "description": "string",
    "instructions": "string",
    "homework_type": "written",
    "due_date": "2025-01-01T00:00:00Z",
    "max_score": 100,
    "is_published": false,
    "metadata": {},
    "id": 0,
    "lesson_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lesson": {
      "title": "string",
      "content": "string",
      "video_url": "string",
      "id": 0,
      "premium_only": true,
      "order": 0,
      "words": []
    }
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/homework/"
```



- __[Endpoint]__ POST /api/v1/homework/
- __[Tavsif]__ yaratish a new homework assignment.
    
    **Required permissions:** Teacher or Admin
    
    **Request Body:**
    - `title`: Title of the homework
    - `description`: Detailed description
    - `instructions`: Instructions for students
    - `homework_type`: Type of homework (written/oral/quiz/project)
    - `due_date`: Due date (ISO 8601 format)
    - `course_id`: ID of the course
    - `lesson_id`: Optional ID of the related lesson
    - `oral_assignment`: Required if homework_type is 'oral'
    - `is_published`: Whether to publish immediately
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Form-Data
```json
{
  "title": "string",
  "description": "string",
  "instructions": "string",
  "homework_type": "string",
  "due_date": "2025-01-01T00:00:00Z",
  "course_id": 0,
  "lesson_id": 0,
  "is_published": false,
  "metadata": "{}",
  "oral_assignment": "string",
  "files": [
    "(binary file)"
  ]
}
```

- __[Majburiy maydonlar]__ `title`, `homework_type`, `course_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "instructions": "string",
  "homework_type": "written",
  "due_date": "2025-01-01T00:00:00Z",
  "max_score": 100,
  "is_published": false,
  "metadata": {},
  "id": 0,
  "lesson_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lesson": {
    "title": "string",
    "content": "string",
    "video_url": "string",
    "id": 0,
    "premium_only": true,
    "order": 0,
    "words": []
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/homework/"  \
 -F "title=string"
 -F "description=string"
 -F "instructions=string"
 -F "homework_type=string"
 -F "due_date=2025-01-01T00:00:00Z"
 -F "course_id=0"
 -F "lesson_id=0"
 -F "is_published=False"
 -F "metadata={}"
 -F "oral_assignment=string"
 -F "files=['(binary file)']"
```



- __[Endpoint]__ GET /api/v1/homework/files/{file_id}/download
- __[Tavsif]__ Download a file associated with a homework assignment.
    
    **Required permissions:** Any authenticated user with access to the homework
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__
  - path: `file_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `file_id`
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/homework/files/{file_id}/download"
```



- __[Endpoint]__ POST /api/v1/homework/grade/{user_homework_id}
- __[Tavsif]__ Grade a homework submission with feedback and score.
    
    **Required permissions:** Teacher or Admin
    
    **Parameters:**
    - `user_homework_id`: ID of the user's homework submission to grade
    - `feedback`: Detailed feedback on the submission
    - `score`: Numeric score (0-100)
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_homework_id` (integer) — Majburiy
- __[So‘rov turi]__ Form-UrlEncoded
```json
{
  "feedback": "string",
  "score": 0
}
```

- __[Majburiy maydonlar]__ `user_homework_id`, `feedback`, `score`
- __[Javob namunasi]__
```json
{
  "status": "assigned",
  "submission": {},
  "feedback": "string",
  "score": 0,
  "id": 0,
  "user_id": 0,
  "homework_id": 0,
  "submitted_at": "2025-01-01T00:00:00Z",
  "graded_at": "2025-01-01T00:00:00Z",
  "homework": {
    "title": "string",
    "description": "string",
    "instructions": "string",
    "homework_type": "written",
    "due_date": "2025-01-01T00:00:00Z",
    "max_score": 100,
    "is_published": false,
    "metadata": {},
    "id": 0,
    "lesson_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lesson": {
      "title": "string",
      "content": "string",
      "video_url": "string",
      "id": 0,
      "premium_only": true,
      "order": 0,
      "words": []
    }
  },
  "user": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/homework/grade/{user_homework_id}" -H 'Content-Type: application/x-www-form-urlencoded' -d 'feedback=string&score=0'
```



- __[Endpoint]__ GET /api/v1/homework/lesson/{lesson_id}
- __[Tavsif]__ olish all homework assignments for a specific lesson.
    
    **Required permissions:** Any authenticated user
    
    **Parameters:**
    - `lesson_id`: ID of the lesson to olish homework for
    - `status`: Filter by status (assigned/submitted/graded)
    - `due_soon`: Only return assignments due in the next X days
    - `skip`: Number of records to skip (for pagination)
    - `limit`: Maximum number of records to return (for pagination)
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__
  - path: `lesson_id` (integer) — Majburiy
  - query: `status` (string) — Ixtiyoriy
  - query: `due_soon` (integer) — Ixtiyoriy
  - query: `include_files` (boolean) — Ixtiyoriy
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `lesson_id`
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "description": "string",
    "instructions": "string",
    "homework_type": "written",
    "due_date": "2025-01-01T00:00:00Z",
    "max_score": 100,
    "is_published": false,
    "metadata": {},
    "id": 0,
    "lesson_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lesson": {
      "title": "string",
      "content": "string",
      "video_url": "string",
      "id": 0,
      "premium_only": true,
      "order": 0,
      "words": []
    }
  }
]
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/homework/lesson/{lesson_id}"
```



- __[Endpoint]__ GET /api/v1/homework/user/me
- __[Tavsif]__ olish all homework assignments for the currently authenticated user.
    
    **Required permissions:** Any authenticated user
    
    **Parameters:**
    - `skip`: Number of records to skip (for pagination)
    - `limit`: Maximum number of records to return (for pagination)
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "status": "assigned",
    "submission": {},
    "feedback": "string",
    "score": 0,
    "id": 0,
    "user_id": 0,
    "homework_id": 0,
    "submitted_at": "2025-01-01T00:00:00Z",
    "graded_at": "2025-01-01T00:00:00Z",
    "homework": {
      "title": "string",
      "description": "string",
      "instructions": "string",
      "homework_type": "written",
      "due_date": "2025-01-01T00:00:00Z",
      "max_score": 100,
      "is_published": false,
      "metadata": {},
      "id": 0,
      "lesson_id": 0,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z",
      "lesson": {
        "title": "string",
        "content": "string",
        "video_url": "string",
        "id": 0,
        "premium_only": true,
        "order": 0,
        "words": []
      }
    },
    "user": {
      "email": "string",
      "is_active": true,
      "is_superuser": false,
      "full_name": "string",
      "current_level": "string",
      "last_viewed_lesson_id": 0,
      "id": 0,
      "roles": [],
      "is_premium": true,
      "role": "free"
    }
  }
]
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/homework/user/me"
```



- __[Endpoint]__ GET /api/v1/homework/{homework_id}
- __[Tavsif]__ olish homework details by its ID.
    
    **Required permissions:** Any authenticated user
    
    **Parameters:**
    - `homework_id`: ID of the homework to olish
    - `include_submissions`: Include student submissions (teacher/admin only)
    - `include_files`: Include file URLs (signed URLs for S3)
- __[Auth]__ Ha (Admin/Superuser)
- __[Parametrlar]__
  - path: `homework_id` (integer) — Majburiy
  - query: `include_submissions` (boolean) — Ixtiyoriy
  - query: `include_files` (boolean) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `homework_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "instructions": "string",
  "homework_type": "written",
  "due_date": "2025-01-01T00:00:00Z",
  "max_score": 100,
  "is_published": false,
  "metadata": {},
  "id": 0,
  "lesson_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "lesson": {
    "title": "string",
    "content": "string",
    "video_url": "string",
    "id": 0,
    "premium_only": true,
    "order": 0,
    "words": []
  }
}
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/homework/{homework_id}"
```



- __[Endpoint]__ POST /api/v1/homework/{homework_id}/assign/{user_id}
- __[Tavsif]__ Assign a specific homework to a user.
    
    **Required permissions:** Teacher or Admin
    
    **Parameters:**
    - `homework_id`: ID of the homework to assign
    - `user_id`: ID of the user to assign the homework to
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `homework_id` (integer) — Majburiy
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `homework_id`, `user_id`
- __[Javob namunasi]__
```json
{
  "status": "assigned",
  "submission": {},
  "feedback": "string",
  "score": 0,
  "id": 0,
  "user_id": 0,
  "homework_id": 0,
  "submitted_at": "2025-01-01T00:00:00Z",
  "graded_at": "2025-01-01T00:00:00Z",
  "homework": {
    "title": "string",
    "description": "string",
    "instructions": "string",
    "homework_type": "written",
    "due_date": "2025-01-01T00:00:00Z",
    "max_score": 100,
    "is_published": false,
    "metadata": {},
    "id": 0,
    "lesson_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lesson": {
      "title": "string",
      "content": "string",
      "video_url": "string",
      "id": 0,
      "premium_only": true,
      "order": 0,
      "words": []
    }
  },
  "user": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/homework/{homework_id}/assign/{user_id}"
```



- __[Endpoint]__ POST /api/v1/homework/{homework_id}/submit
- __[Tavsif]__ Submit a homework assignment.
    
    **Required permissions:** Any authenticated user (must be assigned the homework)
    
    **Parameters:**
    - `homework_id`: ID of the homework to submit
    - `submission`: Text submission (required)
    - `files`: Optional files to upload with the submission
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__
  - path: `homework_id` (integer) — Majburiy
- __[So‘rov turi]__ Form-Data
```json
{
  "submission": "string",
  "files": [
    "(binary file)"
  ]
}
```

- __[Majburiy maydonlar]__ `homework_id`, `submission`
- __[Javob namunasi]__
```json
{
  "status": "assigned",
  "submission": {},
  "feedback": "string",
  "score": 0,
  "id": 0,
  "user_id": 0,
  "homework_id": 0,
  "submitted_at": "2025-01-01T00:00:00Z",
  "graded_at": "2025-01-01T00:00:00Z",
  "homework": {
    "title": "string",
    "description": "string",
    "instructions": "string",
    "homework_type": "written",
    "due_date": "2025-01-01T00:00:00Z",
    "max_score": 100,
    "is_published": false,
    "metadata": {},
    "id": 0,
    "lesson_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lesson": {
      "title": "string",
      "content": "string",
      "video_url": "string",
      "id": 0,
      "premium_only": true,
      "order": 0,
      "words": []
    }
  },
  "user": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/homework/{homework_id}/submit" -H "Authorization: Bearer <TOKEN>"  \
 -F "submission=string"
 -F "files=['(binary file)']"
```



- __[Endpoint]__ POST /api/v1/homework/{homework_id}/submit-oral
- __[Tavsif]__ Submit an oral homework assignment by uploading an audio file.
    
    **Required permissions:** Any authenticated user (must be assigned the homework)
    
    **Parameters:**
    - `homework_id`: ID of the homework to submit
    - `audio_file`: Audio file to upload
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__
  - path: `homework_id` (integer) — Majburiy
- __[So‘rov turi]__ Form-Data
```json
{
  "audio_file": "(binary file)"
}
```

- __[Majburiy maydonlar]__ `homework_id`, `audio_file`
- __[Javob namunasi]__
```json
{
  "content": "string",
  "file_url": "string",
  "audio_url": "string",
  "id": 0,
  "homework_id": 0,
  "student_id": 0,
  "status": "pending",
  "score": 0,
  "feedback": "string",
  "submitted_at": "2025-01-01T00:00:00Z",
  "graded_at": "2025-01-01T00:00:00Z",
  "graded_by": 0,
  "student": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  },
  "homework": {
    "title": "string",
    "description": "string",
    "instructions": "string",
    "homework_type": "written",
    "due_date": "2025-01-01T00:00:00Z",
    "max_score": 100,
    "is_published": false,
    "metadata": {},
    "id": 0,
    "lesson_id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "lesson": {
      "title": "string",
      "content": "string",
      "video_url": "string",
      "id": 0,
      "premium_only": true,
      "order": 0,
      "words": []
    }
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/homework/{homework_id}/submit-oral" -H "Authorization: Bearer <TOKEN>"  \
 -F "audio_file=(binary file)"
```



## info
- __[Endpoint]__ GET /version
- __[Tavsif]__ olish Version
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/version"
```



## interactive-lessons
- __[Endpoint]__ GET /api/v1/interactive-lessons/
- __[Tavsif]__ olish list of interactive lessons available to the user
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "order": 0,
    "description": "string",
    "video_url": "string",
    "difficulty": "beginner",
    "is_premium": false,
    "is_active": true,
    "content": {},
    "tags": [
      "string"
    ],
    "estimated_duration": 0,
    "id": 0,
    "course_id": 0,
    "avatar_id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/interactive-lessons/"
```



- __[Endpoint]__ POST /api/v1/interactive-lessons/assess-pronunciation
- __[Tavsif]__ Analyze and assess user's pronunciation.
    
    - Accepts audio recording
    - Compares with expected text
    - Returns detailed pronunciation feedback
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Form-Data
```json
{
  "expected_text": "string",
  "audio_file": "(binary file)"
}
```

- __[Majburiy maydonlar]__ `expected_text`, `audio_file`
- __[Javob namunasi]__
```json
{
  "recognized_text": "string",
  "pronunciation_score": 0,
  "feedback": "string",
  "word_scores": {
    "<key>": 0
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/interactive-lessons/assess-pronunciation"  \
 -F "expected_text=string"
 -F "audio_file=(binary file)"
```



- __[Endpoint]__ POST /api/v1/interactive-lessons/send-audio-message
- __[Tavsif]__ Handles the full voice-to-voice interaction cycle.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Form-Data
```json
{
  "session_id": 0,
  "audio_file": "(binary file)"
}
```

- __[Majburiy maydonlar]__ `session_id`, `audio_file`
- __[Javob namunasi]__
```json
{
  "text": "string",
  "audio_url": "string",
  "avatar_type": "string",
  "avatar_name": "string",
  "suggestions": [
    "string"
  ]
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/interactive-lessons/send-audio-message"  \
 -F "session_id=0"
 -F "audio_file=(binary file)"
```



- __[Endpoint]__ POST /api/v1/interactive-lessons/send-message
- __[Tavsif]__ Send a message to the AI tutor and olish a response.
    
    - Processes user message
    - Generates AI response
    - Returns text and optional audio response
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "session_id": 0,
  "message": "string",
  "message_type": "text"
}
```

- __[Majburiy maydonlar]__ `session_id`, `message`
- __[Javob namunasi]__
```json
{
  "text": "string",
  "audio_url": "string",
  "avatar_type": "string",
  "avatar_name": "string",
  "suggestions": [
    "string"
  ]
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/interactive-lessons/send-message" \
 -H 'Content-Type: application/json' -d '{"session_id": 0, "message": "string", "message_type": "text"}'
```



- __[Endpoint]__ POST /api/v1/interactive-lessons/start-lesson
- __[Tavsif]__ Start a new interactive lesson session with an AI tutor.
    
    - Creates a new lesson session
    - Initializes AI tutor with selected avatar
    - Returns session details and initial greeting
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "lesson_type": "conversation",
  "topic": "string",
  "difficulty": "beginner",
  "avatar_type": "default"
}
```

- __[Majburiy maydonlar]__ `lesson_type`
- __[Javob namunasi]__
```json
{
  "id": 0,
  "user_id": 0,
  "lesson_type": "conversation",
  "started_at": "2025-01-01T00:00:00Z",
  "status": "in_progress",
  "avatar_type": "string",
  "greeting": "string",
  "avatar_name": "string",
  "audio_url": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/interactive-lessons/start-lesson" \
 -H 'Content-Type: application/json' -d '{"lesson_type": "conversation", "topic": "string", "difficulty": "beginner", "avatar_type": "default"}'
```



- __[Endpoint]__ GET /api/v1/interactive-lessons/{lesson_id}
- __[Tavsif]__ interaktiv darsni ID bo‘yicha olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `lesson_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `lesson_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "order": 0,
  "description": "string",
  "video_url": "string",
  "difficulty": "beginner",
  "is_premium": false,
  "is_active": true,
  "content": {},
  "tags": [
    "string"
  ],
  "estimated_duration": 0,
  "id": 0,
  "course_id": 0,
  "avatar_id": 0
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/interactive-lessons/{lesson_id}"
```



## lesson-interactions
- __[Endpoint]__ POST /api/v1/lesson-interactions/{session_id}/interact
- __[Tavsif]__ yaratish a new interaction in a lesson session.
    
    This endpoint accepts either text input or an audio file for speech-to-text conversion.
    The AI will process the input and generate an appropriate response.
    
    **Note**: Either `user_input` or `audio_file` must be provided.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `session_id` (integer) — Majburiy
- __[So‘rov turi]__ Form-Data
```json
{
  "user_input": "string",
  "audio_file": "(binary file)"
}
```

- __[Majburiy maydonlar]__ `session_id`, `user_input`
- __[Javob namunasi]__
```json
{
  "user_message": "string",
  "ai_response": "string",
  "id": 0,
  "session_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/lesson-interactions/{session_id}/interact"  \
 -F "user_input=string"
 -F "audio_file=(binary file)"
```



- __[Endpoint]__ GET /api/v1/lesson-interactions/{session_id}/interactions
- __[Tavsif]__ olish interactions for a specific lesson session.
    
    Returns a paginated list of interactions between the user and AI tutor.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `session_id` (integer) — Majburiy
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `session_id`
- __[Javob namunasi]__
```json
[
  {
    "user_message": "string",
    "ai_response": "string",
    "id": 0,
    "session_id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/lesson-interactions/{session_id}/interactions"
```



## lessons
- __[Endpoint]__ GET /api/v1/lessons/
- __[Tavsif]__ lessonsni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "content": "string",
    "video_url": "string",
    "id": 0,
    "premium_only": true,
    "order": 0,
    "words": []
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/lessons/"
```



- __[Endpoint]__ POST /api/v1/lessons/
- __[Tavsif]__ Yangi lessons yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "content": "string",
  "video_url": "string",
  "course_id": 0,
  "order": 0,
  "premium_only": false
}
```

- __[Majburiy maydonlar]__ `title`, `content`, `course_id`, `order`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "content": "string",
  "video_url": "string",
  "id": 0,
  "premium_only": true,
  "order": 0,
  "words": []
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/lessons/" \
 -H 'Content-Type: application/json' -d '{"title": "string", "content": "string", "video_url": "string", "course_id": 0, "order": 0, "premium_only": false}'
```



- __[Endpoint]__ DELETE /api/v1/lessons/{id}
- __[Tavsif]__ lessonsni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "content": "string",
  "video_url": "string",
  "id": 0,
  "premium_only": true,
  "order": 0,
  "words": []
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/lessons/{id}"
```



- __[Endpoint]__ GET /api/v1/lessons/{id}
- __[Tavsif]__ lessonsni ID bo‘yicha olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "content": "string",
  "video_url": "string",
  "id": 0,
  "premium_only": true,
  "order": 0,
  "words": []
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/lessons/{id}"
```



- __[Endpoint]__ PUT /api/v1/lessons/{id}
- __[Tavsif]__ lessonsni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "title": "string",
  "content": "string",
  "video_url": "string",
  "order": 0,
  "premium_only": true
}
```

- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "content": "string",
  "video_url": "string",
  "id": 0,
  "premium_only": true,
  "order": 0,
  "words": []
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/lessons/{id}" \
 -H 'Content-Type: application/json' -d '{"title": "string", "content": "string", "video_url": "string", "order": 0, "premium_only": true}'
```



## login
- __[Endpoint]__ POST /api/v1/login
- __[Tavsif]__ Foydalanuvchini tizimga kiritadi va access token qaytaradi.
Swagger UI da avtomatik authorize bo'ladi.

Faqat username va password kerak.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "username": "string",
  "password": "string"
}
```

- __[Majburiy maydonlar]__ `username`, `password`
- __[Javob namunasi]__
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "string",
  "expires_in": 0,
  "scope": "string",
  "success": true,
  "message": "string",
  "user": {
    "id": 0,
    "username": "string",
    "email": "string",
    "phone_number": "string"
  },
  "location_info": {
    "ip": "string",
    "country": "string",
    "region": "string",
    "city": "string",
    "timezone": "string",
    "current_time": "string",
    "utc_offset": "string",
    "display_time": "string",
    "login_time": "string"
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/login" \
 -H 'Content-Type: application/json' -d '{"username": "string", "password": "string"}'
```



- __[Endpoint]__ GET /api/v1/login/test-token
- __[Tavsif]__ Test access token
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/login/test-token"
```



## metrics
- __[Endpoint]__ GET /api/v1/metrics
- __[Tavsif]__ Expose Prometheus metrics for monitoring the application.

This endpoint returns metrics in the Prometheus exposition format.
Access is restricted to authenticated users with appropriate permissions.
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/metrics"
```



- __[Endpoint]__ GET /api/v1/metrics/health
- __[Tavsif]__ Health check endpoint for monitoring services.
Returns a simple status message indicating the service is running.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "<key>": "string"
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/metrics/health"
```



- __[Endpoint]__ GET /api/v1/metrics/status
- __[Tavsif]__ olish detailed system status information.
Autentifikatsiya talab qilinadi.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/metrics/status"
```



## notifications
- __[Endpoint]__ GET /api/v1/notifications/
- __[Tavsif]__ notificationsni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
  - query: `is_read` (boolean) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "id": 0,
    "user_id": 0,
    "message": "string",
    "is_read": true,
    "created_at": "2025-01-01T00:00:00Z",
    "notification_type": "general",
    "data": {}
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/notifications/"
```



- __[Endpoint]__ POST /api/v1/notifications/read-all
- __[Tavsif]__ Mark all of the user's notifications as read.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "msg": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/notifications/read-all"
```



- __[Endpoint]__ GET /api/v1/notifications/unread-count
- __[Tavsif]__ olish the count of unread notifications joriy foydalanuvchi uchun.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "unread_count": 0
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/notifications/unread-count"
```



- __[Endpoint]__ POST /api/v1/notifications/{notification_id}/read
- __[Tavsif]__ Mark a specific notification as read.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `notification_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `notification_id`
- __[Javob namunasi]__
```json
{
  "id": 0,
  "user_id": 0,
  "message": "string",
  "is_read": true,
  "created_at": "2025-01-01T00:00:00Z",
  "notification_type": "general",
  "data": {}
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/notifications/{notification_id}/read"
```



## payments
- __[Endpoint]__ GET /api/v1/payments/
- __[Tavsif]__ olish user's payment history and subscription information.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  "string"
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/payments/"
```



- __[Endpoint]__ POST /api/v1/payments/create-checkout-session
- __[Tavsif]__ yaratish a Stripe Checkout Session for subscription.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `subscription_plan_id` (integer) — Majburiy
  - query: `success_url` (string) — Majburiy
  - query: `cancel_url` (string) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `subscription_plan_id`, `success_url`, `cancel_url`
- __[Javob namunasi]__
```json
{}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/payments/create-checkout-session"
```



- __[Endpoint]__ POST /api/v1/payments/webhook/stripe
- __[Tavsif]__ Handle Stripe webhook events for payment processing.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - header: `stripe-signature` (string) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/payments/webhook/stripe"
```



## statistics
- __[Endpoint]__ GET /api/v1/statistics/
- __[Tavsif]__ olish general platform statistics for authenticated users.
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{}
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/statistics/"
```



- __[Endpoint]__ GET /api/v1/statistics/payment-stats
- __[Tavsif]__ olish payment statistics, such as total revenue and active subscriptions.
(Admin only)
- __[Auth]__ Ha (Admin/Superuser)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{}
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/statistics/payment-stats"
```



- __[Endpoint]__ GET /api/v1/statistics/top-users
- __[Tavsif]__ olish the top users by the number of completed lessons.
(Admin only)
- __[Auth]__ Ha (Admin/Superuser)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "lesson_count": 0,
    "role": "free"
  }
]
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/statistics/top-users"
```



## subscription-plans
- __[Endpoint]__ GET /api/v1/subscription-plans/
- __[Tavsif]__ Barcha obuna rejalarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "name": "string",
    "price": 0,
    "duration_days": 0,
    "description": "string",
    "stripe_price_id": "string",
    "gpt4o_requests_quota": 0,
    "stt_requests_quota": 0,
    "tts_chars_quota": 0,
    "pronunciation_analysis_quota": 0,
    "id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/subscription-plans/"
```



- __[Endpoint]__ POST /api/v1/subscription-plans/
- __[Tavsif]__ Yangi obuna reja yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0
}
```

- __[Majburiy maydonlar]__ `name`, `price`, `duration_days`, `stripe_price_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0,
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/subscription-plans/" \
 -H 'Content-Type: application/json' -d '{"name": "string", "price": 0, "duration_days": 0, "description": "string", "stripe_price_id": "string", "gpt4o_requests_quota": 0, "stt_requests_quota": 0, "tts_chars_quota": 0, "pronunciation_analysis_quota": 0}'
```



- __[Endpoint]__ DELETE /api/v1/subscription-plans/{plan_id}
- __[Tavsif]__ obuna rejani o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `plan_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `plan_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0,
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/subscription-plans/{plan_id}"
```



- __[Endpoint]__ GET /api/v1/subscription-plans/{plan_id}
- __[Tavsif]__ obuna rejani ID bo‘yicha olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `plan_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `plan_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0,
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/subscription-plans/{plan_id}"
```



- __[Endpoint]__ PUT /api/v1/subscription-plans/{plan_id}
- __[Tavsif]__ obuna rejani yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `plan_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0
}
```

- __[Majburiy maydonlar]__ `plan_id`
- __[Javob namunasi]__
```json
{
  "name": "string",
  "price": 0,
  "duration_days": 0,
  "description": "string",
  "stripe_price_id": "string",
  "gpt4o_requests_quota": 0,
  "stt_requests_quota": 0,
  "tts_chars_quota": 0,
  "pronunciation_analysis_quota": 0,
  "id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/subscription-plans/{plan_id}" \
 -H 'Content-Type: application/json' -d '{"name": "string", "price": 0, "duration_days": 0, "description": "string", "stripe_price_id": "string", "gpt4o_requests_quota": 0, "stt_requests_quota": 0, "tts_chars_quota": 0, "pronunciation_analysis_quota": 0}'
```



## subscriptions
- __[Endpoint]__ GET /api/v1/subscriptions/
- __[Tavsif]__ Barcha obunalarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "plan_id": 0,
    "end_date": "2025-01-01T00:00:00Z",
    "is_active": true,
    "id": 0,
    "user_id": 0,
    "start_date": "2025-01-01T00:00:00Z",
    "plan": {
      "name": "string",
      "price": 0,
      "duration_days": 0,
      "description": "string",
      "stripe_price_id": "string",
      "gpt4o_requests_quota": 0,
      "stt_requests_quota": 0,
      "tts_chars_quota": 0,
      "pronunciation_analysis_quota": 0,
      "id": 0
    }
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/subscriptions/"
```



- __[Endpoint]__ POST /api/v1/subscriptions/create-checkout-session
- __[Tavsif]__ yaratish a Stripe checkout session for a subscription plan.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "plan_id": 0
}
```

- __[Majburiy maydonlar]__ `plan_id`
- __[Javob namunasi]__
```json
{
  "id": "string",
  "url": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/subscriptions/create-checkout-session" \
 -H 'Content-Type: application/json' -d '{"plan_id": 0}'
```



- __[Endpoint]__ GET /api/v1/subscriptions/me
- __[Tavsif]__ olish the current user's subscriptions.
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "plan_id": 0,
    "end_date": "2025-01-01T00:00:00Z",
    "is_active": true,
    "id": 0,
    "user_id": 0,
    "start_date": "2025-01-01T00:00:00Z",
    "plan": {
      "name": "string",
      "price": 0,
      "duration_days": 0,
      "description": "string",
      "stripe_price_id": "string",
      "gpt4o_requests_quota": 0,
      "stt_requests_quota": 0,
      "tts_chars_quota": 0,
      "pronunciation_analysis_quota": 0,
      "id": 0
    }
  }
]
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/subscriptions/me"
```



- __[Endpoint]__ GET /api/v1/subscriptions/plans
- __[Tavsif]__ olish available subscription plans for authenticated users.
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "name": "string",
    "price": 0,
    "duration_days": 0,
    "description": "string",
    "stripe_price_id": "string",
    "gpt4o_requests_quota": 0,
    "stt_requests_quota": 0,
    "tts_chars_quota": 0,
    "pronunciation_analysis_quota": 0,
    "id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/subscriptions/plans"
```



- __[Endpoint]__ POST /api/v1/subscriptions/stripe-webhook
- __[Tavsif]__ Stripe webhook endpoint to handle payment events.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - header: `stripe-signature` (string) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/subscriptions/stripe-webhook"
```



- __[Endpoint]__ GET /api/v1/subscriptions/users/{user_id}/subscriptions
- __[Tavsif]__ olish a specific user's subscriptions. (Admin only)
- __[Auth]__ Ha (Admin/Superuser)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
[
  {
    "plan_id": 0,
    "end_date": "2025-01-01T00:00:00Z",
    "is_active": true,
    "id": 0,
    "user_id": 0,
    "start_date": "2025-01-01T00:00:00Z",
    "plan": {
      "name": "string",
      "price": 0,
      "duration_days": 0,
      "description": "string",
      "stripe_price_id": "string",
      "gpt4o_requests_quota": 0,
      "stt_requests_quota": 0,
      "tts_chars_quota": 0,
      "pronunciation_analysis_quota": 0,
      "id": 0
    }
  }
]
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/subscriptions/users/{user_id}/subscriptions"
```



- __[Endpoint]__ POST /api/v1/subscriptions/users/{user_id}/subscriptions
- __[Tavsif]__ Yangi obuna yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
  - query: `plan_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `user_id`, `plan_id`
- __[Javob namunasi]__
```json
{
  "plan_id": 0,
  "end_date": "2025-01-01T00:00:00Z",
  "is_active": true,
  "id": 0,
  "user_id": 0,
  "start_date": "2025-01-01T00:00:00Z",
  "plan": {
    "name": "string",
    "price": 0,
    "duration_days": 0,
    "description": "string",
    "stripe_price_id": "string",
    "gpt4o_requests_quota": 0,
    "stt_requests_quota": 0,
    "tts_chars_quota": 0,
    "pronunciation_analysis_quota": 0,
    "id": 0
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/subscriptions/users/{user_id}/subscriptions"
```



- __[Endpoint]__ DELETE /api/v1/subscriptions/{subscription_id}
- __[Tavsif]__ obunani o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `subscription_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `subscription_id`
- __[Javob namunasi]__
```json
{
  "plan_id": 0,
  "end_date": "2025-01-01T00:00:00Z",
  "is_active": true,
  "id": 0,
  "user_id": 0,
  "start_date": "2025-01-01T00:00:00Z",
  "plan": {
    "name": "string",
    "price": 0,
    "duration_days": 0,
    "description": "string",
    "stripe_price_id": "string",
    "gpt4o_requests_quota": 0,
    "stt_requests_quota": 0,
    "tts_chars_quota": 0,
    "pronunciation_analysis_quota": 0,
    "id": 0
  }
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/subscriptions/{subscription_id}"
```



## tests
- __[Endpoint]__ GET /api/v1/tests/
- __[Tavsif]__ Barcha testlarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "description": "string",
    "test_type": "ielts",
    "duration_minutes": 0,
    "is_active": true,
    "id": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "sections": []
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/tests/"
```



- __[Endpoint]__ GET /api/v1/tests/attempts/me
- __[Tavsif]__ Barcha meni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "test_id": 0,
    "user_id": 0,
    "id": 0,
    "start_time": "2025-01-01T00:00:00Z",
    "end_time": "2025-01-01T00:00:00Z",
    "time_spent_seconds": 0,
    "is_completed": false,
    "total_score": 0.0,
    "max_score": 0.0,
    "answers": [],
    "user": {
      "email": "string",
      "is_active": true,
      "is_superuser": false,
      "full_name": "string",
      "current_level": "string",
      "last_viewed_lesson_id": 0,
      "id": 0,
      "roles": [],
      "is_premium": true,
      "role": "free"
    }
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/tests/attempts/me"
```



- __[Endpoint]__ GET /api/v1/tests/attempts/{attempt_id}
- __[Tavsif]__ attemptsni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `attempt_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `attempt_id`
- __[Javob namunasi]__
```json
{
  "test_id": 0,
  "user_id": 0,
  "id": 0,
  "start_time": "2025-01-01T00:00:00Z",
  "end_time": "2025-01-01T00:00:00Z",
  "time_spent_seconds": 0,
  "is_completed": false,
  "total_score": 0.0,
  "max_score": 0.0,
  "answers": [],
  "user": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  }
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/tests/attempts/{attempt_id}"
```



- __[Endpoint]__ POST /api/v1/tests/attempts/{attempt_id}/finish
- __[Tavsif]__ Finish a test attempt and olish the final results.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `attempt_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `attempt_id`
- __[Javob namunasi]__
```json
{
  "attempt_id": 0,
  "test_id": 0,
  "test_title": "string",
  "total_score": 0,
  "max_score": 0,
  "percentage": 0,
  "is_passed": true,
  "sections": [
    {
      "section_id": 0,
      "section_title": "string",
      "score": 0,
      "max_score": 0,
      "answers": [
        {
          "question_id": 0,
          "user_answer": "string",
          "correct_answer": "string",
          "is_correct": true,
          "score": 0
        }
      ]
    }
  ],
  "feedback": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/tests/attempts/{attempt_id}/finish"
```



- __[Endpoint]__ POST /api/v1/tests/attempts/{attempt_id}/submit
- __[Tavsif]__ Submit answers for a test attempt.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `attempt_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
[
  {
    "question_id": 0,
    "answer_data": {},
    "attempt_id": 0
  }
]
```

- __[Majburiy maydonlar]__ `attempt_id`
- __[Javob namunasi]__
```json
{
  "msg": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/tests/attempts/{attempt_id}/submit" \
 -H 'Content-Type: application/json' -d '[{"question_id": 0, "answer_data": {}, "attempt_id": 0}]'
```



- __[Endpoint]__ GET /api/v1/tests/{test_id}
- __[Tavsif]__ olish a specific test by ID, with all its sections and questions.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `test_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `test_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "description": "string",
  "test_type": "ielts",
  "duration_minutes": 0,
  "is_active": true,
  "id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "sections": []
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/tests/{test_id}"
```



- __[Endpoint]__ POST /api/v1/tests/{test_id}/start
- __[Tavsif]__ Start a new test attempt joriy foydalanuvchi uchun. Premium users only.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `test_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `test_id`
- __[Javob namunasi]__
```json
{
  "test_id": 0,
  "user_id": 0,
  "id": 0,
  "start_time": "2025-01-01T00:00:00Z",
  "end_time": "2025-01-01T00:00:00Z",
  "time_spent_seconds": 0,
  "is_completed": false,
  "total_score": 0.0,
  "max_score": 0.0,
  "answers": [],
  "user": {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  }
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/tests/{test_id}/start"
```



## user-progress
- __[Endpoint]__ GET /api/v1/user-progress/
- __[Tavsif]__ Barcha user progressni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "user_id": 0,
    "lesson_id": 0,
    "id": 0,
    "completed_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/user-progress/"
```



- __[Endpoint]__ POST /api/v1/user-progress/lessons/{lesson_id}/complete
- __[Tavsif]__ Mark a lesson as complete joriy foydalanuvchi uchun.
If the lesson completes a course, a certificate is generated.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `lesson_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `lesson_id`
- __[Javob namunasi]__
```json
{
  "user_id": 0,
  "lesson_id": 0,
  "id": 0,
  "completed_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/user-progress/lessons/{lesson_id}/complete"
```



## users
- __[Endpoint]__ GET /api/v1/users/
- __[Tavsif]__ foydalanuvchilarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "email": "string",
    "is_active": true,
    "is_superuser": false,
    "full_name": "string",
    "current_level": "string",
    "last_viewed_lesson_id": 0,
    "id": 0,
    "roles": [],
    "is_premium": true,
    "role": "free"
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/users/"
```



- __[Endpoint]__ POST /api/v1/users/
- __[Tavsif]__ Yangi foydalanuvchi yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - header: `g-recaptcha-response` (string) — Ixtiyoriy
- __[So‘rov turi]__ JSON
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "username": "string",
  "password": "string"
}
```

- __[Majburiy maydonlar]__ `email`, `username`, `password`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/users/" \
 -H 'Content-Type: application/json' -d '{"email": "string", "is_active": true, "is_superuser": false, "full_name": "string", "current_level": "string", "last_viewed_lesson_id": 0, "username": "string", "password": "string"}'
```



- __[Endpoint]__ GET /api/v1/users/certificates/
- __[Tavsif]__ sertifikatlarni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "title": "string",
    "user_id": 0,
    "course_id": 0,
    "course_name": "string",
    "level_completed": "string",
    "description": "string",
    "verification_code": "string",
    "id": 0,
    "issue_date": "2025-01-01T00:00:00Z",
    "is_valid": true,
    "file_path": "string"
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/users/certificates/"
```



- __[Endpoint]__ GET /api/v1/users/certificates/{certificate_id}
- __[Tavsif]__ Download a certificate PDF.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `certificate_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `certificate_id`
- __[Javob namunasi]__
```json
string
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/users/certificates/{certificate_id}"
```



- __[Endpoint]__ POST /api/v1/users/courses/{course_id}/complete
- __[Tavsif]__ Mark a course as completed and generate a certificate.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `course_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `course_id`
- __[Javob namunasi]__
```json
{
  "title": "string",
  "user_id": 0,
  "course_id": 0,
  "course_name": "string",
  "level_completed": "string",
  "description": "string",
  "verification_code": "string",
  "id": 0,
  "issue_date": "2025-01-01T00:00:00Z",
  "is_valid": true,
  "file_path": "string"
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/users/courses/{course_id}/complete"
```



- __[Endpoint]__ GET /api/v1/users/me
- __[Tavsif]__ olish current user.
- __[Auth]__ Ha (JWT)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/users/me"
```



- __[Endpoint]__ PATCH /api/v1/users/me
- __[Tavsif]__ meni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "email": "string",
  "username": "string",
  "full_name": "string",
  "current_level": "string",
  "password": "string",
  "roles": [
    "string"
  ]
}
```

- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -X PATCH "http://0.0.0.0:8004/api/v1/users/me" \
 -H 'Content-Type: application/json' -d '{"email": "string", "username": "string", "full_name": "string", "current_level": "string", "password": "string", "roles": ["string"]}'
```



- __[Endpoint]__ GET /api/v1/users/me/next-lesson
- __[Tavsif]__ olish the next lesson joriy foydalanuvchi uchun to continue learning.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "title": "string",
  "content": "string",
  "video_url": "string",
  "id": 0,
  "premium_only": true,
  "order": 0,
  "words": []
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/users/me/next-lesson"
```



- __[Endpoint]__ GET /api/v1/users/me/premium-data
- __[Tavsif]__ Fetch premium data joriy foydalanuvchi uchun. Requires active subscription.
(Admins can also access this route)
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "msg": "string"
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/users/me/premium-data"
```



- __[Endpoint]__ GET /api/v1/users/test-superuser
- __[Tavsif]__ Test endpoint that only superusers can access.
- __[Auth]__ Ha (Admin/Superuser)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{
  "msg": "string"
}
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/users/test-superuser"
```



- __[Endpoint]__ DELETE /api/v1/users/{user_id}
- __[Tavsif]__ foydalanuvchini o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/users/{user_id}"
```



- __[Endpoint]__ GET /api/v1/users/{user_id}
- __[Tavsif]__ olish a specific user by ID (Superuser only).
- __[Auth]__ Ha (Admin/Superuser)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -H "Authorization: Bearer <TOKEN>" "http://0.0.0.0:8004/api/v1/users/{user_id}"
```



- __[Endpoint]__ PUT /api/v1/users/{user_id}
- __[Tavsif]__ foydalanuvchini yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `user_id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "email": "string",
  "username": "string",
  "full_name": "string",
  "current_level": "string",
  "password": "string",
  "roles": [
    "string"
  ]
}
```

- __[Majburiy maydonlar]__ `user_id`
- __[Javob namunasi]__
```json
{
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "full_name": "string",
  "current_level": "string",
  "last_viewed_lesson_id": 0,
  "id": 0,
  "roles": [],
  "is_premium": true,
  "role": "free"
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/users/{user_id}" \
 -H 'Content-Type: application/json' -d '{"email": "string", "username": "string", "full_name": "string", "current_level": "string", "password": "string", "roles": ["string"]}'
```



## webrtc
- __[Endpoint]__ POST /api/v1/webrtc/rooms/create
- __[Tavsif]__ yaratish a new video call room.

- **name**: Room name (optional)
- **is_private**: Whether the room Autentifikatsiya talab qilinadi. (default: True)
- **max_participants**: Maximum number of participants (default: 10)
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{}
```

- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
{}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/webrtc/rooms/create" \
 -H 'Content-Type: application/json' -d '{}'
```



- __[Endpoint]__ POST /api/v1/webrtc/rooms/{room_id}/end
- __[Tavsif]__ End a room and disconnect all users
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `room_id` (string) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `room_id`
- __[Javob]__ Ko‘rsatilmagan
- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/webrtc/rooms/{room_id}/end"
```



- __[Endpoint]__ GET /api/v1/webrtc/rooms/{room_id}/users
- __[Tavsif]__ olish list of users in a room
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `room_id` (string) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `room_id`
- __[Javob namunasi]__
```json
[
  {}
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/webrtc/rooms/{room_id}/users"
```



## words
- __[Endpoint]__ GET /api/v1/words/
- __[Tavsif]__ wordsni olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - query: `skip` (integer) — Ixtiyoriy
  - query: `limit` (integer) — Ixtiyoriy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ Yo‘q
- __[Javob namunasi]__
```json
[
  {
    "word": "string",
    "translation": "string",
    "ipa_pronunciation": "string",
    "id": 0,
    "lesson_id": 0
  }
]
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/words/"
```



- __[Endpoint]__ POST /api/v1/words/
- __[Tavsif]__ Yangi words yaratish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__ Yo‘q
- __[So‘rov turi]__ JSON
```json
{
  "word": "string",
  "translation": "string",
  "ipa_pronunciation": "string",
  "lesson_id": 0
}
```

- __[Majburiy maydonlar]__ `word`, `translation`, `lesson_id`
- __[Javob namunasi]__
```json
{
  "word": "string",
  "translation": "string",
  "ipa_pronunciation": "string",
  "id": 0,
  "lesson_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X POST "http://0.0.0.0:8004/api/v1/words/" \
 -H 'Content-Type: application/json' -d '{"word": "string", "translation": "string", "ipa_pronunciation": "string", "lesson_id": 0}'
```



- __[Endpoint]__ DELETE /api/v1/words/{id}
- __[Tavsif]__ wordsni o‘chirish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "word": "string",
  "translation": "string",
  "ipa_pronunciation": "string",
  "id": 0,
  "lesson_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X DELETE "http://0.0.0.0:8004/api/v1/words/{id}"
```



- __[Endpoint]__ GET /api/v1/words/{id}
- __[Tavsif]__ wordsni ID bo‘yicha olish.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ Yo‘q
- __[Majburiy maydonlar]__ `id`
- __[Javob namunasi]__
```json
{
  "word": "string",
  "translation": "string",
  "ipa_pronunciation": "string",
  "id": 0,
  "lesson_id": 0
}
```

- __[cURL namunasi]__
```bash
curl "http://0.0.0.0:8004/api/v1/words/{id}"
```



- __[Endpoint]__ PUT /api/v1/words/{id}
- __[Tavsif]__ wordsni yangilash.
- __[Auth]__ Yo‘q (agar ko‘rsatilmagan bo‘lsa)
- __[Parametrlar]__
  - path: `id` (integer) — Majburiy
- __[So‘rov turi]__ JSON
```json
{
  "word": "string",
  "translation": "string",
  "ipa_pronunciation": "string"
}
```

- __[Majburiy maydonlar]__ `id`, `word`, `translation`
- __[Javob namunasi]__
```json
{
  "word": "string",
  "translation": "string",
  "ipa_pronunciation": "string",
  "id": 0,
  "lesson_id": 0
}
```

- __[cURL namunasi]__
```bash
curl -X PUT "http://0.0.0.0:8004/api/v1/words/{id}" \
 -H 'Content-Type: application/json' -d '{"word": "string", "translation": "string", "ipa_pronunciation": "string"}'
 
 ```
 - __[cURL namunasi]__
 [Endpoint] POST /api/v1/ai/analyze-answer
[Tavsif] Foydalanuvchi matnli javobini tahlil qilib, strukturali fikr-mulohaza (grammar, vocabulary, pronunciation, fluency, overall) qaytaradi.
[Auth] Yo‘q (jamoat endpointi)
[Parametrlar] Yo‘q
[So‘rov turi] JSON


```bash
{
  "user_response": "Men bugun dars qildim va ingliz tilida gapirdim.",
  "reference_text": "Today I studied and spoke in English.",
  "context": {
    "lesson_id": 123,
    "topic": "Daily routine"
  },
  "feedback_types": ["all"], 
  "language": "en-US"
}
 ```

javob namujnasi

```bash
{
  "feedback_id": "a9a2f4b2-1b4e-4f3a-9b67-1b8d2a9f1c23",
  "timestamp": "2025-08-22T08:42:11.000Z",
  "grammar": {
    "score": 78.5,
    "feedback": "Grammar looks decent. Watch basic sentence structure and agreement.",
    "corrections": [],
    "error_types": null
  },
  "vocabulary": {
    "score": 70.0,
    "feedback": "Try to diversify vocabulary and match key terms from the reference.",
    "suggestions": ["today"],
    "advanced_words": [],
    "misused_words": []
  },
  "pronunciation": {
    "score": 70.0,
    "feedback": "Without audio we estimate pronunciation; try clear stress and pacing.",
    "tips": [
      "Speak slowly and clearly",
      "Emphasize key content words",
      "Practice difficult sounds using minimal pairs"
    ],
    "problem_sounds": [],
    "stress_patterns": null
  },
  "fluency": {
    "score": 72.0,
    "feedback": "Aim for natural rhythm and avoid long pauses.",
    "suggestions": [
      "Use linking words (however, therefore, moreover)",
      "Keep sentences concise"
    ],
    "pace": "just right",
    "hesitation_markers": null
  },
  "overall": {
    "score": 72.6,
    "feedback": "Good effort. Focus on aligning content with the reference and clarity.",
    "next_steps": [
      "Re-read the reference, note 3 key terms, and include them in your answer",
      "Record a 30s response focusing on clarity and grammar"
    ],
    "strengths": ["Relevant content"],
    "areas_for_improvement": ["Content alignment", "Sentence structure", "Vocabulary range"]
  },
  "audio_feedback_url": null,
  "metadata": {
    "overlap": 34.62,
    "user_token_count": 9,
    "ref_token_count": 7,
    "language": "en-US"
  }
}
 ```




-[Endpoint] POST /api/v1/ai/voice-loop
-
[Tavsif] Yuborilgan audio nutqni matnga aylantiradi (STT), matnni AI yordamida tahlil qiladi (strukturali feedback), so‘ng AI javobini ovozga o‘girib MP3 URL qaytaradi (TTS).
[Auth] JWT talab qilinadi (foydalanuvchi autentifikatsiyasi). Quota tekshiruvlari ishlaydi.
[Rate limit] 20/min (limiter)
[Quota tekshiruvi]
STT: stt_requests_left ≥ 1
AI text gen: gpt4o_requests_left ≥ 1
TTS: tts_chars_left javob uzunligiga yetarli bo‘lishi kerak
[Parametrlar]
form: file (audio/*) — Majburiy
form: 
language
 (string) — Ixtiyoriy, standart: uz
form: reference_text (string) — Ixtiyoriy (AI tahlilini etalon matn bilan boyitish uchun)
[So‘rov turi] multipart/form-data



[Javob namunasi]
 ```bash
{
  "transcript": "Hello, this is a test message",
  "ai_text": "Good effort. Focus on aligning content with the reference and clarity.",
  "corrections": ["..."],
  "advice": [
    "Re-read the reference, note 3 key terms, and include them in your answer",
    "Record a 30s response focusing on clarity and grammar"
  ],
  "audio_url": "/uploads/tts/voice_loop_1_1692691200.mp3",
  "feedback": {
    "feedback_id": "b4f6c3a2-9e11-4a5f-9a0b-1c2d3e4f5a6b",
    "timestamp": "2025-08-22T08:55:00Z",
    "grammar": {"score": 78.5, "feedback": "Grammar looks decent.", "corrections": [], "error_types": null},
    "vocabulary": {"score": 70.0, "feedback": "Try to diversify vocabulary.", "suggestions": [], "advanced_words": [], "misused_words": []},
    "pronunciation": {"score": 70.0, "feedback": "Estimated from text only.", "tips": ["Speak slowly"], "problem_sounds": [], "stress_patterns": null},
    "fluency": {"score": 72.0, "feedback": "Aim for natural rhythm.", "suggestions": ["Use linking words"], "pace": "just right", "hesitation_markers": null},
    "overall": {"score": 72.6, "feedback": "Good effort.", "next_steps": ["Re-read reference"], "strengths": ["Relevant content"], "areas_for_improvement": ["Content alignment"]},
    "audio_feedback_url": null,
    "metadata": {"overlap": 34.62, "user_token_count": 6, "ref_token_count": 7, "language": "uz"}
  },
  "quotas": {
    "stt_requests_left": 9,
    "gpt4o_requests_left": 49,
    "tts_chars_left": 9500
  },
  "timestamp": "2025-08-22T08:55:00Z"
}
 ```


-[Endpoint] POST /api/v1/ai-sessions/sessions

[Tavsif] Yangi AI sessiya yaratish (multi-turn chat uchun).
[Auth] JWT talab qilinadi (get_current_active_user)
[Parametrlar]
query: title (string) — Ixtiyoriy
[So‘rov turi] Yo‘q
[Javob namunasi]

 ```bash
{
  "id": "7b3f2c8e1d4b4f3a8e3c9c1b2a0d4f6e",
  "user_id": 1,
  "title": "AI Session",
  "status": "idle",
  "created_at": "2025-08-22T09:05:00Z",
  "messages": []
}
 ```


[Endpoint] POST /api/v1/ai/usage/reset
[Tavsif] Ko‘rsatilgan user_id uchun qolgan AI kvotalarini roll/subskriptiyaga mos holda qayta o‘rnatadi.
[Auth] Admin JWT talab qilinadi (get_current_active_admin)
[Parametrlar]
query: user_id (int) — Majburiy
[So‘rov turi] Yo‘q (faqat query param)
[Ishlash mantiqi]
Premium foydalanuvchi: agar faol obuna va unda plan bo‘lsa, plan kvotalari qo‘llanadi.
Premium, plansiz fallback: gpt4o=500, tts_chars=100000, stt=2000, pronunciation=400.
Free foydalanuvchi: gpt4o=50, tts_chars=5000, stt=100, pronunciation=20.
Foydalanuvchi topilmasa: mavjud usage yozuvi o‘zgarmagan holda qaytadi (xato qaytarmaydi).
[Javob turi] 


 ```bash

id (int)
user_id (int)
usage_date (datetime)
gpt4o_requests_left (int)
stt_requests_left (int)
tts_chars_left (int)
pronunciation_analysis_left (int)

 ```

[Endpoint] POST /api/v1/ai-sessions/sessions/{session_id}/messages [Tavsif] Foydalanuvchi xabarini (matn yoki audio) yuboradi. Audio bo‘lsa STT → AI tahlil → LLM javob → ixtiyoriy TTS. Sessiyaga ikkita xabar qo‘shiladi: user va assistant. [Auth] JWT talab qilinadi; AI kvotasi tekshiruvi: gpt4o_requests_left ≥ 1 [Parametrlar] path: session_id (string) — Majburiy form: text (string) — Ixtiyoriy, audio bo‘lmasa majburiy form: audio_file (audio/*) — Ixtiyoriy, text bo‘lmasa majburiy form: speak (boolean) — Ixtiyoriy, standart: false (TTS yoqish) form: language (string) — Ixtiyoriy, standart: uz form: reference_text (string) — Ixtiyoriy (foydalanuvchi javobini shu matn bilan tahlil qilish) [So‘rov turi] multipart/form-data [Quota tekshiruvi] AI: gpt4o_requests_left ≥ 1 (majburiy) STT: stt_requests_left ≥ 1 (faqat audio yuborilganda) TTS: tts_chars_left ≥ assistant_text uzunligi (faqat speak=true bo‘lsa)



Javob namunasi
 ```bash

{
  "session": {
    "id": "sess_abc123",
    "user_id": 1,
    "title": "AI Session",
    "status": "idle",
    "created_at": "2025-08-22T09:05:00Z",
    "messages": [
      {
        "role": "user",
        "text": "Hello",
        "audio_url": null,
        "analysis": { /* AIFeedbackResponse */ },
        "created_at": "2025-08-22T09:05:10Z"
      },
      {
        "role": "assistant",
        "text": "Salom! Bugun qanday yordam bera olaman?",
        "audio_url": "/uploads/tts/sess_<id>_<ts>.mp3",
        "analysis": null,
        "created_at": "2025-08-22T09:05:11Z"
      }
    ]
  },
  "assistant": {
    "text": "Salom! Bugun qanday yordam bera olaman?",
    "audio_url": "/uploads/tts/sess_<id>_<ts>.mp3"
  },
  "user_analysis": { /* AIFeedbackResponse */ }
}

 ```



AI Sessions — sessiyalarni boshqarish
[Endpoint] GET /api/v1/ai-sessions/sessions
[Tavsif] Foydalanuvchining barcha sessiyalari ro‘yxati (eng so‘nggi yaratilgan birinchi).
[Auth] JWT talab qilinadi
[Parametrlar] Yo‘q
[Javob namunasi]


 ```bash

{
  "sessions": [
    {
      "id": "7b3f2c8e1d4b4f3a8e3c9c1b2a0d4f6e",
      "user_id": 1,
      "title": "AI Session",
      "status": "idle",
      "created_at": "2025-08-22T09:05:00Z",
      "messages": []
    }
  ],
  "count": 1
}
 ```




[Endpoint] GET /api/v1/ai-sessions/sessions/{session_id}
[Tavsif] Bitta sessiyani to‘liq tarix bilan olish.
[Auth] JWT talab qilinadi
[Parametrlar]
path: session_id (string) — Majburiy
[Javob namunasi] Sessiya obyekti (yuqoridagiga o‘xshash, 
messages
 bilan)
[Xatoliklar] 404 — Sessiya topilmadi yoki foydalanuvchiga tegishli emas
[cURL]



 ```bash

curl "http://0.0.0.0:8004/api/v1/ai-sessions/sessions/<SESSION_ID>" \
 -H "Authorization: Bearer <TOKEN>"
 ```


[Endpoint] PATCH /api/v1/ai-sessions/sessions/{session_id}
[Tavsif] Sessiya metama’lumotlarini yangilash (masalan, sarlavha yoki holat).
[Auth] JWT talab qilinadi
[Parametrlar]
path: session_id (string) — Majburiy
[So‘rov turi] multipart/form-data
form: title (string) — Ixtiyoriy
form: status (string) — Ixtiyoriy
[Javob] Yangilangan sessiya obyekti
[Xatoliklar] 404 — Sessiya topilmadi yoki foydalanuvchiga tegishli emas
[cURL]


 ```bash

curl -X PATCH "http://0.0.0.0:8004/api/v1/ai-sessions/sessions/<SESSION_ID>" \
 -H "Authorization: Bearer <TOKEN>" \
 -F "title=My New Title"
 ```



[Endpoint] DELETE /api/v1/ai-sessions/sessions/{session_id}
[Tavsif] Sessiyani o‘chirish.
[Auth] JWT talab qilinadi
[Parametrlar]
path: session_id (string) — Majburiy
[Javob namunasi]


 ```bash
{"status": "deleted", "id": "<SESSION_ID>"}
 ```


[Endpoint] POST /api/v1/ai-sessions/sessions/{session_id}/reset
[Tavsif] Sessiya ichidagi barcha xabarlarni tozalaydi, statusni idlega qaytaradi.
[Auth] JWT talab qilinadi
[Parametrlar]
path: session_id (string) — Majburiy
[Javob] Tozalangan sessiya obyekti (
messages
: [])
[Xatoliklar] 404 — Sessiya topilmadi yoki foydalanuvchiga tegishli emas
[cURL]

 ```bash
curl -X POST "http://0.0.0.0:8004/api/v1/ai-sessions/sessions/<SESSION_ID>/reset" \
 -H "Authorization: Bearer <TOKEN>"

 ```