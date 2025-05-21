import ollama

from config import *
from connector import run_query
import queries
from books import get_embedding
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

    assistant_reply = response['message']['content']
    threads[thread_id].append({'role': 'assistant', 'content': assistant_reply})
    run_query(queries.insert_message, {'uuid': thread_id, 'role': 2, 'message': assistant_reply})

    return assistant_reply


async def ask_question(thread_id: str, data: str):
    """Функция отвечает на запросы пользователя, используя список литературы из базы знаний"""
    if thread_id not in threads:
        threads[thread_id] = [
            {
                'role': 'system',
                'content': helper_instructions
            }
        ]
        run_query(queries.insert_session, {'user_id': 1, 'uuid': thread_id, 'mode_id': 2})

    # Добавляем сообщение пользователя в историю
    run_query(queries.insert_message, {'uuid': thread_id, 'role': 1, 'message': str(data)})

    # Получаем embedding запроса и находим релевантные источники
    embedding = get_embedding(str(data))
    sources = run_query(queries.select_sources, {'emb': str(embedding)})

    # Формируем контекст из источников
    context = "\n\n".join(
        f"[Источник: {row['name']}: {row['text']}]"
        for row in sources
    )

    # Строим новый список сообщений: инструкции, контекст, вопрос
    messages = [{'role': 'system', 'content': helper_instructions},
                {"role": "system", "content": f"Вот выдержки из книг, которые могут тебе пригодиться:\n\n{context}"},
                {'role': 'user', 'content': str(data)}]

    # Получаем ответ от модели
    response = ollama.chat(
        model=model,
        messages=messages,
        keep_alive='10m',
        options={"temperature": 0.2}
    )

    # Сохраняем ответ в истории
    assistant_reply = response['message']['content']
    threads[thread_id].append({'role': 'assistant', 'content': assistant_reply})
    run_query(queries.insert_message, {'uuid': thread_id, 'role': 2, 'message': assistant_reply})

    return assistant_reply