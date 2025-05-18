import ollama

from config import *
from connector import run_query
import queries
# Храним историю чатов
threads = {}

async def load_model():
    loaded = ollama.chat(model=model, messages=[], keep_alive='10m')
async def talk_to_assistant(thread_id: str, data: str):
    """Функция ведет историю чата в рамках одного thread_id."""
    
    if thread_id not in threads:
        threads[thread_id] = [
            {
                'role': 'system',
                'content': instructions
            }
        ]
        run_query(queries.insert_session, {'user_id': 1, 'uuid': thread_id, 'mode_id': 1})

    # Добавляем сообщение пользователя в историю
    threads[thread_id].append({'role': 'user', 'content': str(data)})
    run_query(queries.insert_message, {'uuid': thread_id, 'role': 1, 'message': str(data)})

    # Запрашиваем у Ollama ответ с учетом всей истории
    response = ollama.chat(model=model, messages=threads[thread_id], keep_alive='10m')

    # Добавляем ответ ассистента в историю
    threads[thread_id].append({'role': 'assistant', 'content': response['message']['content']})
    run_query(queries.insert_message, {'uuid': thread_id, 'role': 2, 'message': response['message']['content']})
    
    return response['message']['content']
