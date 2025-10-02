from fastapi import FastAPI
from app.database import Base, engine
from app import models

# Створення таблиць
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud Notes API - Dev")

@app.get("/")
async def root():
    return {"message": "Cloud Notes API — OK"}

