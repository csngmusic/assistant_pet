from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
from assistant import *


class EchoRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Эхо для GET-запроса
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Echo: {self.path}".encode('utf-8'))  # Отправляем обратно путь запроса

    def do_POST(self):
        # Эхо для POST-запроса
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        assistant_query = post_data.decode()
        assistant_response = talk_to_assistant(assistant_query)
        response = assistant_response['message']['content']
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Echo: {response}".encode('utf-8'))  # Отправляем обратно данные из POST

server_address = ("0.0.0.0", 8443)  # Слушаем на всех интерфейсах
httpd = HTTPServer(server_address, EchoRequestHandler)

# Создаем SSLContext
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

# Оборачиваем сокет с использованием SSLContext
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("HTTPS-сервер с эхо запущен на порту 8443...")
httpd.serve_forever()
