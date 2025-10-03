# main.py — головний вхідний файл застосунку

# Імпорти основних залежностей
from fastapi import FastAPI                 # Фреймворк для створення API
from app.database import Base, engine         # База даних: декларативна база та підключення (SQLAlchemy)
from app.routes import users, notes                  # Імпорт роутів (endpoints) для користувачів


# Створення таблиць у базі даних
# Якщо таблиць ще немає — вони будуть створені
Base.metadata.create_all(bind=engine)


# Ініціалізація FastAPI-додатку
app = FastAPI(title="Cloud Notes API - Dev")  # Назва відображатиметься в Swagger UI

# Підключення роутів
app.include_router(users.router)              # Реєстрація всіх endpoint з users
app.include_router(notes.router)

# Тестовий маршрут
# Перевірка працездатності API
@app.get("/")
async def root():
    return {"message": "Cloud Notes API — OK"}

