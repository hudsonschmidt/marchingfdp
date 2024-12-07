import socket
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler
import os
import signal
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except FileNotFoundError:
            file_to_open = "File Not Found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

def handle_client(client_socket, client_addr):
    logging.info(f"Client connected: {client_addr}")
    try:
        request = client_socket.recv(1024).decode()
        if not request:
            return

        # Parse HTTP headers
        headers = request.split('\n')
        first_header_components = headers[0].split()

        if len(first_header_components) < 2:
            return

        http_method = first_header_components[0]
        path = first_header_components[1]

        if http_method == 'GET':
            if path == '/':
                try:
                    with open('index.html', 'r') as fin:
                        content = fin.read()
                    response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + content
                except FileNotFoundError:
                    response = 'HTTP/1.1 404 Not Found\n\nFile Not Found'
            else:
                response = 'HTTP/1.1 404 Not Found\n\nFile Not Found'
        else:
            response = 'HTTP/1.1 405 Method Not Allowed\nAllow: GET\n\nMethod Not Allowed'

        client_socket.sendall(response.encode())
    except Exception as e:
        logging.error(f"Error handling client {client_addr}: {e}")
    finally:
        client_socket.close()
        logging.info(f"Client disconnected: {client_addr}")

def start_server():
    HOST = "0.0.0.0"
    PORT = 8989
    BACKLOG = 10

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allows address to be reused immediately

    server_socket.bind((HOST, PORT))
    server_socket.listen(BACKLOG)
    logging.info(f"Server created on port: {PORT}\nWaiting for connections...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            client_socket, client_addr = server_socket.accept()
            executor.submit(handle_client, client_socket, client_addr)

def signal_handler(signal, frame):
    logging.info('Shutting down server...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_server()
