from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import FileResponse
from assistant import talk_to_assistant

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
async def search_question(query: QueryModel, request: Request):
    thread_id = request.client.host  # Получаем IP клиента
    try:
        answer: str = await talk_to_assistant(thread_id, query.question)
    except Exception as e:
        answer = str(e)
    return {"answer": answer}

# @app.get("/")
# async def home():
#     return {"message": "Добро пожаловать на главную страницу!"}