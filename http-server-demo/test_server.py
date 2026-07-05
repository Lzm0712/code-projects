"""Pytest unit tests for the HTTP server."""

import pytest
import socket
import threading
import time
from server import HTTPServer


@pytest.fixture
def server():
    """Create a test server instance with a unique port."""
    srv = HTTPServer(host='127.0.0.1', port=0)  # port=0 lets OS pick an available port
    thread = srv.start(background=True)
    # Wait for server to start and get assigned port
    time.sleep(0.3)
    yield srv
    # Cleanup handled by daemon thread


def send_raw_request(host, port, request):
    """Send a raw HTTP request and return the response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((host, port))
    sock.sendall(request.encode('utf-8'))
    response = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break
    sock.close()
    return response.decode('utf-8')


class TestHTTPServer:
    """Test cases for HTTPServer."""

    def test_home_route(self, server):
        """Test the home route returns welcome message."""
        request = f"GET / HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        assert "200 OK" in response
        assert "Welcome to Simple HTTP Server" in response

    def test_hello_route(self, server):
        """Test the hello route returns greeting."""
        request = f"GET /hello HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        assert "200 OK" in response
        assert "Hello, World!" in response

    def test_hello_route_with_name(self, server):
        """Test the hello route with name parameter."""
        request = f"GET /hello?name=Alice HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        assert "200 OK" in response
        assert "Hello, Alice!" in response

    def test_404_route(self, server):
        """Test that unknown routes return 404."""
        request = f"GET /unknown HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        assert "404 Not Found" in response
        assert "Page Not Found" in response

    def test_invalid_request(self, server):
        """Test handling of invalid requests."""
        request = "INVALID REQUEST\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        # Should return 404 or be handled gracefully
        assert "404" in response or "500" in response

    def test_response_headers(self, server):
        """Test that response has correct headers."""
        request = f"GET / HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        assert "HTTP/1.1 200 OK" in response
        assert "Content-Type: text/html" in response
        assert "Content-Length:" in response
        assert "Connection: close" in response

    def test_custom_route(self, server):
        """Test adding and using a custom route."""
        def custom_handler(params=None):
            return '200 OK', '<h1>Custom Route</h1>'

        server.add_route('/custom', custom_handler)
        request = f"GET /custom HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        assert "200 OK" in response
        assert "Custom Route" in response


class TestHTTPMethods:
    """Test HTTP method handling."""

    def test_get_only(self, server):
        """Test that only GET method is supported."""
        request = f"POST / HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n\r\n"
        response = send_raw_request('127.0.0.1', server.port, request)

        # POST to home should return 404 (not in routes)
        assert "404 Not Found" in response
