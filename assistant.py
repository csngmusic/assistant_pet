import ollama

from config import *

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
                'content': 'Сгенерируй ответ на заданный пользователем запрос'
            }
        ]

    # Добавляем сообщение пользователя в историю
    threads[thread_id].append({'role': 'user', 'content': str(data)})

    # Запрашиваем у Ollama ответ с учетом всей истории
    response = ollama.chat(model=model, messages=threads[thread_id], keep_alive='10m')

    # Добавляем ответ ассистента в историю
    threads[thread_id].append({'role': 'assistant', 'content': response['message']['content']})

    return response['message']['content']
