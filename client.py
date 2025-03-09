import requests

while True:
    # URL сервера
    url = "https://192.168.0.227:8443"

    # Данные для отправки
    data = str(input())

    # Отправка POST-запроса (с отключенной проверкой сертификата)
    response = requests.post(url, data=data, verify=False)

    # Выводим ответ
    print("Ответ сервера:", response.text)
