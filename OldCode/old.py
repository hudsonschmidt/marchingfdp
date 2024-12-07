from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()

        self.wfile.write('Hello World!'.encode())

def main():
    PORT = 8989
    server = HTTPServer(('', PORT), handler) # host name, port
    print("Server created on port: ", PORT)
    server.serve_forever()  # will run forever until stopped with control c

if __name__ == '__main__':
    main()