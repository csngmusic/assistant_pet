from fastapi import FastAPI, Request, Cookie, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
import uuid

from assistant import *

# Инициализация FastAPI
app = FastAPI()

# Разрешаем серверу раздавать HTML-файл
app.mount("/static", StaticFiles(directory="static"), name="static")

# Модель запроса
class QueryModel(BaseModel):
    question: str

# Эндпоинт для возврата HTML-страницы
@app.get("/")
async def serve_homepage(request: Request):
    session_id = str(uuid.uuid4())  # Генерируем новый UUID
    response = FileResponse("static/messenger.html")
    response.set_cookie(key="session_id", value=session_id, httponly=False) # UUID -> куки
    await load_model()
    return response

# API для обработки запросов к модели
@app.post("/search/")
async def search_question(query: QueryModel, request: Request, session_id: str = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())  # Генерируем новый, если нет
    try:
        answer = await talk_to_assistant(session_id, query.question)
    except Exception as e:
        answer = str(e)
    return {"answer": answer}

@app.post("/search_literature")
async def search_literature(query: QueryModel, request: Request, session_id: str = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())  # Генерируем новый, если нет
    try:
        answer = await ask_question(session_id, query.question)
    except Exception as e:
        answer = str(e)
    return {"answer": answer}