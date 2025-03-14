from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import FileResponse

# Инициализация FastAPI
app = FastAPI()

# Модель запроса
class QueryModel(BaseModel):
    question: str

# Разрешаем серверу раздавать HTML-файл
app.mount("/static", StaticFiles(directory="static"), name="static")

# Эндпоинт для возврата HTML-страницы
@app.get("/")
async def serve_homepage():
    return FileResponse("static/index.html")

# API для обработки запросов студентов
@app.post("/search/")
async def search_question(query: QueryModel):
    string = query.question.lower()
    return {"answer": f"Вы спросили: {string}"}

# @app.get("/")
# async def home():
#     return {"message": "Добро пожаловать на главную страницу!"}