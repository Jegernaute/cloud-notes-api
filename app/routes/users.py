# routes/users.py — маршрути для управління користувачами (реєстрація та логін)

from fastapi import APIRouter, Depends, HTTPException   # FastAPI — для створення API-роутів
from sqlalchemy.orm import Session                             # Сесія SQLAlchemy для роботи з БД
from app import models, auth                                   # Моделі таблиць та модуль авторизації
from app.database import get_db                                # Функція для підключення до БД
from app.routes.schemas import UserCreate, Token                      # Pydantic-схеми для валідації вхідних даних

# Створення роутера з префіксом `/users`
# У Swagger UI групуватиметься під тегом "users"
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
       Реєстрація нового користувача:
       - Перевірка унікальності email
       - Хешування пароля
       - Створення користувача в БД
       - Повернення JWT-токена
       """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = auth.create_access_token({"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
      Вхід користувача:
      - Перевірка існування користувача
      - Перевірка правильності пароля
      - Повернення JWT-токена
      """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

