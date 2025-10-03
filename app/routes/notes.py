from fastapi import APIRouter, Depends, HTTPException, Header  # Для створення роутів, залежностей та обробки помилок
from sqlalchemy.orm import Session  # Для роботи з базою даних через сесію SQLAlchemy
from typing import List  # Для вказівки типу списку у відповіді
from app.database import get_db  # Функція для отримання сесії бази даних
from app import models  # Моделі таблиць (User, Note)
from app.routes.schemas import NoteCreate, NoteOut  # Pydantic-схеми для валідації вхідних та вихідних даних
from jose import jwt, JWTError  # Для роботи з JWT-токенами

# Створення роутера FastAPI для нотаток
router = APIRouter(prefix="/notes", tags=["notes"])

# Залежність: отримання поточного користувача
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    Отримує користувача за JWT-токеном з заголовка Authorization.
    Повертає об'єкт User або піднімає HTTPException, якщо токен недійсний.
    """
    from app.auth import SECRET_KEY, ALGORITHM  # Секретний ключ і алгоритм для декодування JWT

    # Перевіряємо, чи починається заголовок з "Bearer "
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Відрізаємо "Bearer" для отримання чистого токена
    token = authorization[7:]

    try:
        # Декодуємо JWT-токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")  # Отримуємо email з payload

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Шукаємо користувача у базі даних
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user  # Повертаємо об'єкт користувача
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# CRUD нотаток

# Створення нової нотатки
@router.post("/", response_model=NoteOut)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Створює нову нотатку для поточного користувача.
    Вхід: Pydantic-схема NoteCreate.
    Вихід: Pydantic-схема NoteOut з даними нотатки.
    """
    new_note = models.Note(title=note.title, content=note.content, owner=user)  # Створюємо екземпляр Note
    db.add(new_note)  # Додаємо у сесію
    db.commit()  # Фіксуємо зміни у базі даних
    db.refresh(new_note)  # Оновлюємо екземпляр з даними з бази (наприклад, id)
    return new_note

# Отримання всіх нотаток користувача
@router.get("/", response_model=List[NoteOut])
def get_notes(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Повертає список усіх нотаток поточного користувача.
    """
    return db.query(models.Note).filter(models.Note.user_id == user.id).all()

# Отримання конкретної нотатки по ID
@router.get("/{note_id}", response_model=NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Повертає конкретну нотатку користувача за її ID.
    Якщо нотатку не знайдено — повертає 404.
    """
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# Видалення нотатки по ID
@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Видаляє нотатку користувача за ID.
    Якщо нотатку не знайдено — повертає 404.
    Статус-код 204 означає успішне видалення без тіла відповіді.
    """
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)  # Видаляємо з бази
    db.commit()  # Фіксуємо зміни
    return
