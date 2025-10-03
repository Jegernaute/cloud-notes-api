# database.py — підключення до бази даних через SQLAlchemy

from sqlalchemy import create_engine                   # Створення "двигуна" для підключення до БД
from sqlalchemy.orm import sessionmaker, declarative_base  # Сесії та декларативна база моделей
import os                                              # Робота з системними змінними
from dotenv import load_dotenv                         # Завантаження змінних середовища з .env

# Завантаження .env файлу
load_dotenv() # Підтягуємо конфігурацію (DATABASE_URL, SECRET_KEY тощо)

# Отримуємо URL для підключення до PostgreSQL із .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Друк у консоль для відладки (можна вимкнути після тестів)
print("DATABASE_URL:", DATABASE_URL)

# Налаштування SQLAlchemy

# "engine" — основний об’єкт, що відповідає за підключення до БД
engine = create_engine(DATABASE_URL, echo=True)


# "SessionLocal" — фабрика для створення сесій БД
# autocommit=False → зміни не зберігаються автоматично
# autoflush=False → SQL-запити виконуються лише вручну
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# "Base" — декларативна база, від якої успадковуються всі моделі (User, Note, File)
Base = declarative_base()

# Dependency для FastAPI
def get_db():
    """
        Отримати сесію для роботи з БД.
        Використовується у Depends(), щоб автоматично відкривати/закривати з’єднання.
        """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


