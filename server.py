from fastapi import FastAPI, Request, Cookie
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
import uuid

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
async def serve_homepage(response: JSONResponse):
    session_id = str(uuid.uuid4()) # генерация рандомного ID для сессии
    response.set_cookie(key="session_id", value=session_id, httponly=False) # айди -> куки
    return FileResponse("static/index.html")

# API для обработки запросов студентов
@app.post("/search/")
async def search_question(query: QueryModel, request: Request, session_id: str = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4()) # если нет куки, генерируем новый ID
    try:
        answer: str = await talk_to_assistant(session_id, query.question)
    except Exception as e:
        answer = str(e)
    return {"answer": answer}