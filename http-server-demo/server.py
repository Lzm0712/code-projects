"""Simple HTTP Server with GET support and basic routing."""

import socket
import threading
from urllib.parse import urlparse, parse_qs


class HTTPServer:
    """A simple HTTP server supporting GET requests and basic routing."""

    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.routes = {}
        self._register_default_routes()

    def _register_default_routes(self):
        """Register default routes."""
        self.add_route('/', self._handle_home)
        self.add_route('/hello', self._handle_hello)

    def add_route(self, path, handler):
        """Add a route handler for a given path."""
        self.routes[path] = handler

    def _handle_home(self, params=None):
        """Handle the home route."""
        return '200 OK', '<h1>Welcome to Simple HTTP Server</h1>'

    def _handle_hello(self, params=None):
        """Handle the hello route."""
        name = params.get('name', ['World'])[0] if params else 'World'
        return '200 OK', f'<h1>Hello, {name}!</h1>'

    def _handle_404(self):
        """Handle 404 Not Found."""
        return '404 Not Found', '<h1>404 - Page Not Found</h1>'

    def _parse_request(self, data):
        """Parse HTTP request data."""
        lines = data.split('\r\n')
        if not lines:
            return None, None, None
        request_line = lines[0].split()
        if len(request_line) < 2:
            return None, None, None
        method, path = request_line[0], request_line[1]

        # Parse query parameters
        parsed_url = urlparse(path)
        query_params = parse_qs(parsed_url.query)
        full_path = parsed_url.path

        return method, full_path, query_params

    def _build_response(self, status, content):
        """Build HTTP response."""
        status_text = status.split(' ', 1)[1]
        body = content.encode('utf-8')
        response = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode('utf-8') + body
        return response

    def _handle_client(self, client_socket, client_address):
        """Handle a single client connection."""
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                client_socket.close()
                return

            method, path, params = self._parse_request(data)

            if method == 'GET' and path in self.routes:
                status, content = self.routes[path](params)
            else:
                status, content = self._handle_404()

            response = self._build_response(status, content)
            client_socket.sendall(response)
        except Exception as e:
            try:
                error_response = self._build_response('500 Internal Server Error', '<h1>500 - Internal Server Error</h1>')
                client_socket.sendall(error_response)
            except:
                pass
        finally:
            client_socket.close()

    def start(self, background=False):
        """Start the HTTP server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        # Update port if OS-assigned (port=0)
        if self.port == 0:
            self.port = server_socket.getsockname()[1]
        server_socket.listen(5)

        if background:
            thread = threading.Thread(target=self._run, args=(server_socket,), daemon=True)
            thread.start()
            return thread
        else:
            self._run(server_socket)

    def _run(self, server_socket=None):
        """Run the server (blocking)."""
        if server_socket is None:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
        print(f"Server running on http://{self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            handler = threading.Thread(target=self._handle_client, args=(client_socket, client_address))
            handler.start()


def main():
    """Main entry point."""
    server = HTTPServer(host='0.0.0.0', port=8080)
    server.start()


if __name__ == '__main__':
    main()
