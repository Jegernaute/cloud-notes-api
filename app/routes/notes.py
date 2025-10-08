import uuid
from urllib.parse import urlparse, unquote

from fastapi import APIRouter, Depends, HTTPException, Header, File, UploadFile # Для створення роутів, залежностей та обробки помилок
from fastapi.params import Form
from sqlalchemy import and_
from sqlalchemy.orm import Session  # Для роботи з базою даних через сесію SQLAlchemy
from typing import List, Optional  # Для вказівки типу списку у відповіді
from app.database import get_db  # Функція для отримання сесії бази даних
from app import models  # Моделі таблиць (User, Note)
from app.routes.schemas import NoteOut  # Pydantic-схеми для валідації вхідних та вихідних даних
from jose import jwt, JWTError  # Для роботи з JWT-токенами
from app.services import storage

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
        user = db.query(models.User).filter_by(email=email).first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user  # Повертаємо об'єкт користувача
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# CRUD нотаток

# Отримання всіх нотаток користувача
@router.get("/", response_model=List[NoteOut])
def get_notes(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Повертає список усіх нотаток поточного користувача.
    """
    return db.query(models.Note).filter_by(user_id=user.id).all()

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
        and_(
            models.Note.id == note_id,
            models.Note.user_id == user.id
        )
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# Видалення нотатки по ID разом з файлом у Supabase
@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Видаляє нотатку користувача за ID.
    Якщо нотатку не знайдено — повертає 404.
    Файл з Supabase видаляється перед видаленням запису.
    """
    note = db.query(models.Note).filter(
        and_(
            models.Note.id == note_id,
            models.Note.user_id == user.id
        )
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    #  Видалення файлу у Supabase (якщо є)
    if note.file_url:
        try:
            parsed_path = urlparse(note.file_url).path  # /storage/v1/object/public/notes-files/2/UUID_filename.jpeg
            # Беремо все після 'notes-files/' → '2/UUID_filename.jpeg'
            idx = parsed_path.find("notes-files/")
            if idx == -1:
                raise HTTPException(status_code=500, detail="Invalid file_url format")
            path_inside_bucket = parsed_path[idx + len("notes-files/"):]
            path_inside_bucket = unquote(path_inside_bucket)  # Декодуємо %20 → пробіли
            print(f"[DEBUG] Correct path to delete: '{path_inside_bucket}'")
            storage.remove_file("notes-files", path_inside_bucket)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

    # Видалення запису у базі
    db.delete(note)
    db.commit()
    return



@router.post("/upload", response_model=NoteOut)
def upload_note_file(
    title: str = Form(...),
    content: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """
    Завантаження нової нотатки з файлом у Supabase.
    Використовує унікальні імена файлів, щоб уникнути помилки 409 Duplicate.
    """
    try:
        # Читаємо байти файлу
        file_bytes = file.file.read()

        # Генеруємо унікальне ім'я файлу: user_id/UUID_оригінальна_назва

        unique_filename = f"{user.id}/{uuid.uuid4()}_{file.filename}"

        # Завантажуємо файл у Supabase
        file_url = storage.upload_file("notes-files", unique_filename, file_bytes)

        # Створюємо нову нотатку
        new_note = models.Note(
            title=title,
            content=content,
            file_url=file_url,
            user_id=user.id,
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        return new_note

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


