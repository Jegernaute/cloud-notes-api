# models.py — опис таблиць бази даних через SQLAlchemy ORM

from sqlalchemy import Column, Integer, String, ForeignKey, Text  # Типи полів та зовнішні ключі
from sqlalchemy.orm import relationship                           # Зв’язки між таблицями
from app.database import Base                                     # Базовий клас для моделей

# Таблиця користувачів
class User(Base):
    __tablename__ = "users"# Назва таблиці у БД

    # Поля таблиці
    id = Column(Integer, primary_key=True, index=True)  # Первинний ключ
    email = Column(String, unique=True, index=True, nullable=False)  # Унікальний email
    hashed_password = Column(String, nullable=False)  # Хешований пароль (не зберігаємо відкритий!)

    # Зв’язки
    notes = relationship("Note", back_populates="owner")  # Один користувач → багато нотаток
    files = relationship("File", back_populates="owner")  # Один користувач → багато файлів


# Таблиця нотаток
class Note(Base):
    __tablename__ = "notes"  # Назва таблиці у БД

    # Поля таблиці
    id = Column(Integer, primary_key=True, index=True)   # Первинний ключ
    title = Column(String, nullable=False)               # Заголовок нотатки
    content = Column(Text, nullable=True)                # Текстовий вміст (може бути пустим)

    # Зовнішній ключ
    user_id = Column(Integer, ForeignKey("users.id"))    # Прив’язка до користувача (users.id)

    # Зв’язки
    owner = relationship("User", back_populates="notes") # Зворотній зв’язок до User


# Таблиця файлів
class File(Base):
    __tablename__ = "files"  # Назва таблиці у БД

    # Поля таблиці
    id = Column(Integer, primary_key=True, index=True)   # Первинний ключ
    filename = Column(String, nullable=False)            # Ім’я файлу
    url = Column(String, nullable=False)                 # Шлях/посилання до файлу

    # Зовнішній ключ
    user_id = Column(Integer, ForeignKey("users.id"))    # Прив’язка до користувача (users.id)

    # Зв’язки
    owner = relationship("User", back_populates="files") # Зворотній зв’язок до User
