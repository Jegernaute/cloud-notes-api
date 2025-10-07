from pydantic import BaseModel, EmailStr  # BaseModel для схем, EmailStr для валідації email
from typing import Optional  # Optional для необов'язкових полів


# Схеми для користувачів


class UserCreate(BaseModel):
    """
    Схема для створення користувача:
    Використовується під час реєстрації або логіну.
    Поля:
    - email: валідний email користувача
    - password: пароль у відкритому вигляді
    """
    email: EmailStr
    password: str

class Token(BaseModel):
    """
    Схема відповіді при успішній автентифікації користувача.
    Поля:
    - access_token: JWT токен для подальшої авторизації
    - token_type: тип токена, зазвичай 'bearer'
    """
    access_token: str
    token_type: str

# -----------------------------
# Схеми для нотаток
# -----------------------------

class NoteCreate(BaseModel):
    """
    Схема для створення нової нотатки.
    Поля:
    - title: заголовок нотатки (обов'язкове)
    - content: текст нотатки (необов'язкове)
    """
    title: str
    content: Optional[str] = None
    file_url: Optional[str] = None

class NoteOut(BaseModel):
    """
    Схема для відправки нотатки у відповіді API.
    Поля:
    - id: унікальний ID нотатки
    - title: заголовок нотатки
    - content: текст нотатки (може бути None)
    - user_id: ID користувача-власника
    """
    id: int
    title: str
    content: Optional[str] = None
    user_id: int
    file_url: Optional[str] = None

    class Config:
        orm_mode = True  # Дозволяє Pydantic працювати з ORM-моделями SQLAlchemy
