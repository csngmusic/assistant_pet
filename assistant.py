import ollama

# Храним историю чатов
threads = {}

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

    # Запрашиваем у Ollama ответ с учетом истории
    try:
        response = ollama.chat(model='gemma2:9b', messages=[
            {'role': 'system', 'content': 'Ответь на запрос пользователя'},
            {'role': 'user', 'content': str(data)}
        ])
        return response['message']['content']
    except Exception as e:
        return f"Ошибка: {str(e)}"
    # Добавляем ответ ассистента в историю
    threads[thread_id].append({'role': 'assistant', 'content': response['message']['content']})

    return response['message']['content']
