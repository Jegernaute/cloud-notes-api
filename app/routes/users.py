# routes/users.py — маршрути для управління користувачами (реєстрація та логін)

from fastapi import APIRouter, Depends, HTTPException, status   # FastAPI — для створення API-роутів
from sqlalchemy.orm import Session                             # Сесія SQLAlchemy для роботи з БД
from app import models, auth                                   # Моделі таблиць та модуль авторизації
from app.database import get_db                                # Функція для підключення до БД
from pydantic import BaseModel, EmailStr                       # Pydantic-схеми для валідації вхідних даних

# Створення роутера з префіксом `/users`
# У Swagger UI групуватиметься під тегом "users"
router = APIRouter(prefix="/users", tags=["users"])

# # Pydantic-схеми (валідація даних)
class UserCreate(BaseModel):
    """Схема для створення користувача (реєстрація/логін)."""
    email: EmailStr  # Валідація email
    password: str  # Пароль у відкритому вигляді (буде захешований)

class Token(BaseModel):
    """Схема відповіді при успішній аутентифікації."""
    access_token: str  # JWT-токен
    token_type: str  # Тип токена (наприклад, "bearer")

# Реєстрація користувача
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
       Реєстрація нового користувача:
       - Перевірка, чи email вже існує
       - Хешування пароля
       - Збереження користувача у базу
       - Генерація JWT-токена для нового користувача
       """
    # Перевірка унікальності email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Хешування пароля
    hashed = auth.hash_password(user.password)

    # Створення нового користувача
    new_user = models.User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Генерація токена для нового користувача
    token = auth.create_access_token({"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

# Логін користувача
@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
       Вхід користувача (автентифікація):
       - Перевірка існування користувача
       - Перевірка правильності пароля
       - Генерація JWT-токена при успішному вході
       """
    # Шукаємо користувача за email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    # Якщо користувача не існує або пароль неправильний
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Якщо все гаразд — створюємо токен
    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
