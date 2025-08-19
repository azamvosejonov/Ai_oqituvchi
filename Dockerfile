# Python'ning rasmiy versiyasidan boshlaymiz
FROM python:3.13-slim

# Konteyner ichidagi ishchi papkani belgilaymiz
WORKDIR /app

# Talablar faylini nusxalaymiz
COPY ./requirements.txt /app/requirements.txt

# Kerakli paketlarni o'rnatamiz
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Qolgan barcha kodlarni nusxalaymiz
COPY . /app

# Tashqi dunyo uchun 8002 portini ochamiz
EXPOSE 8002

# Ilovani ishga tushirish buyrug'i
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
