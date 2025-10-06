# Використовуємо офіційний lightweight Python образ
FROM python:3.12-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо requirements.txt у контейнер
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проєкт у контейнер
COPY . .

# Вказуємо команду запуску
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
