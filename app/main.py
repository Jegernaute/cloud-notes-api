from fastapi import FastAPI

app = FastAPI(title="Cloud Notes API - Dev")

@app.get("/")
async def root():
    return {"message": "Cloud Notes API — OK"}

