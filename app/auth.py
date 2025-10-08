# auth.py — модуль для безпеки та роботи з автентифікацією

# Імпорти основних залежностей
import os                                 # Робота зі змінними середовища
from datetime import datetime, timedelta  # Час для налаштування тривалості дії токенів
from jose import jwt            # Бібліотека для створення та перевірки JWT токенів
from passlib.hash import bcrypt  # Для безпечного хешування паролів
from dotenv import load_dotenv            # Завантаження змінних середовища з .env файлу

# Завантаження змінних середовища з файлу .env
load_dotenv()

# Конфігурація безпеки
SECRET_KEY = os.getenv("SECRET_KEY", "change_me")  # Секретний ключ для підпису токенів
ALGORITHM = "HS256"                                # Алгоритм шифрування токенів
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24              # Час життя токену (1 день)

# Хешування пароля
def hash_password(password: str) -> str:
    """
        Хешування пароля за допомогою bcrypt.
        Використовується при реєстрації або зміні пароля.
        """
    # обмежуємо довжину пароля до 72 символів
    return bcrypt.hash(password[:72])


def verify_password(plain_password, hashed_password):
    """
        Перевірка пароля:
        - Порівнює введений користувачем пароль із хешем у базі.
        """
    return bcrypt.verify(plain_password[:72], hashed_password)


# Створення JWT токену
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
        Створює JWT токен:
        - Приймає словник даних (наприклад, {"sub": user.email})
        - Додає час життя токену (за замовчуванням — 1 день)
        - Повертає зашифрований токен
        """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
