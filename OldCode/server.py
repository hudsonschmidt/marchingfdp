from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import threading

def main():
    HOST = "0.0.0.0"
    PORT = 8989
    BACKLOG = 10

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allows address to be reused immediately

    server_socket.bind((HOST, PORT))
    server_socket.listen(BACKLOG)

    print(f"Server created on port: {PORT}\nWaiting for connections...")

    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()

def handle_client(client_socket, client_addr):
    BUFFER = 1024
    print("Connected!")
    print(f"Client address: {client_addr}")
    request = client_socket.recv(BUFFER).decode()
    print(request)

    # Returns HTTP response
    headers = request.split('\n')
    first_header_components = headers[0].split()

    http_method = first_header_components[0]
    path = first_header_components[1]

    if http_method == 'GET':
        try:
            if path == '/':
                with open('index.html', 'r') as fin:
                    content = fin.read()
                response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + content
            else:
                # handle the edge case, for simplicity return 404
                response = 'HTTP/1.1 404 Not Found\n\nFile Not Found'
        except FileNotFoundError:
            response = 'HTTP/1.1 404 Not Found\n\nFile Not Found'
    else:
        response = 'HTTP/1.1 405 Method Not Allowed\nAllow: GET\n\nMethod Not Allowed'

    client_socket.sendall(response.encode())
    client_socket.close()

if __name__ == "__main__":
    main()
