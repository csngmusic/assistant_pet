import chromadb
import json
import os
import ollama
from config import *

# Инициализация ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="methodical_docs")

# Функция загрузки JSON-файлов
def load_json_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                content = json.load(file)
                data.append({"filename": filename, "text": content["text"]})
    return data

# Загрузка и индексация методичек
json_data = load_json_files("methodics/")
for idx, doc in enumerate(json_data):
    collection.add(
        ids=[str(idx)],
        metadatas=[{"filename": doc["filename"]}],
        documents=[doc["text"]]
    )
print("Методички загружены в ChromaDB!")

# Функция поиска в методичках и генерации ответа
def search_in_docs(query):
    results = collection.query(query_texts=[query], n_results=3)
    retrieved_texts = [doc for doc in results["documents"][0]]

    # Формируем запрос для Ollama (Gemma 2)
    prompt = f"""
    Вопрос студента: "{query}"
    В методичках найдены такие фрагменты:
    {retrieved_texts}

    На основе этих данных, сформулируй понятный ответ для студента.
    """

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]
