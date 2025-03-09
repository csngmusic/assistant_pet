import ollama

def talk_to_assistant(data):
    response = ollama.chat(model='gemma2:9b', messages=[
        {
            'role': 'system',
            'content': 'Сгенерируй ответ на заданный пользователем запрос'
        },
        { 
            'role': 'user',
            'content': str(data)
        }
    ])
    return response