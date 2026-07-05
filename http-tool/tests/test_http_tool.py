"""
HTTP Tool 单元测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http_tool import parse_args, parse_headers, format_response, send_request


class TestParseArgs:
    def test_get_method(self):
        with patch("sys.argv", ["http_tool.py", "GET", "http://example.com"]):
            args = parse_args()
            assert args.method == "GET"
            assert args.url == "http://example.com"

    def test_post_method_with_headers(self):
        with patch("sys.argv", ["http_tool.py", "POST", "http://example.com", "-H", "Content-Type: application/json"]):
            args = parse_args()
            assert args.method == "POST"
            assert args.headers == ["Content-Type: application/json"]

    def test_put_method_with_body(self):
        with patch("sys.argv", ["http_tool.py", "PUT", "http://example.com", "-d", '{"name":"test"}']):
            args = parse_args()
            assert args.method == "PUT"
            assert args.body == '{"name":"test"}'

    def test_delete_method(self):
        with patch("sys.argv", ["http_tool.py", "DELETE", "http://example.com"]):
            args = parse_args()
            assert args.method == "DELETE"

    def test_multiple_headers(self):
        with patch("sys.argv", ["http_tool.py", "POST", "http://example.com", "-H", "Content-Type: application/json", "-H", "Authorization: Bearer token"]):
            args = parse_args()
            assert len(args.headers) == 2


class TestParseHeaders:
    def test_empty_headers(self):
        assert parse_headers(None) == {}
        assert parse_headers([]) == {}

    def test_single_header(self):
        result = parse_headers(["Content-Type: application/json"])
        assert result == {"Content-Type": "application/json"}

    def test_multiple_headers(self):
        result = parse_headers([
            "Content-Type: application/json",
            "Authorization: Bearer token123"
        ])
        assert result == {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123"
        }

    def test_header_value_with_colons(self):
        result = parse_headers(["Server: nginx:1.19"])
        assert result == {"Server": "nginx:1.19"}

    def test_header_trim_whitespace(self):
        result = parse_headers(["Content-Type:  application/json  "])
        assert result == {"Content-Type": "application/json"}


class TestFormatResponse:
    def test_json_response(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"name": "test", "value": 123}'
        with patch("sys.stdout", new_callable=MagicMock) as mock_stdout:
            format_response(mock_response)
            output = mock_stdout.write.call_args_list
            full_output = ''.join([str(call) for call in output])
            assert "Status: 200" in full_output

    def test_non_json_response(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"Hello World"
        with patch("sys.stdout", new_callable=MagicMock) as mock_stdout:
            format_response(mock_response)


class TestSendRequest:
    @patch("http_tool.request.urlopen")
    def test_get_request_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"result": "ok"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        send_request("GET", "http://example.com")
        
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_method() == "GET"
        assert req.full_url == "http://example.com"

    @patch("http_tool.request.urlopen")
    def test_post_request_with_body(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 201
        mock_response.read.return_value = b'{"id": 1}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        send_request("POST", "http://example.com", body='{"name":"test"}')
        
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_method() == "POST"
        assert req.data == b'{"name":"test"}'

    @patch("http_tool.request.urlopen")
    def test_post_request_with_headers(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"{}"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        headers = {"Content-Type": "application/json", "Authorization": "Bearer token"}
        send_request("POST", "http://example.com", headers=headers)
        
        mock_urlopen.assert_called_once()
        # 验证请求方法为 POST
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_method() == "POST"
        # 验证 headers 被正确传递（通过 header_items 检查）
        header_items = dict(req.header_items())
        assert header_items.get("Content-type") == "application/json"
        assert header_items.get("Authorization") == "Bearer token"

    @patch("http_tool.request.urlopen")
    def test_put_request(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"updated": true}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        send_request("PUT", "http://example.com/1", body='{"name":"updated"}')
        
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_method() == "PUT"

    @patch("http_tool.request.urlopen")
    def test_delete_request(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 204
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        send_request("DELETE", "http://example.com/1")
        
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_method() == "DELETE"

    @patch("http_tool.request.urlopen")
    def test_http_error(self, mock_urlopen):
        from urllib.error import HTTPError
        
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.read.return_value = b'{"error": "Not Found"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        
        error = HTTPError(
            url="http://example.com",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=mock_response
        )
        mock_urlopen.side_effect = error
        
        with patch("sys.exit") as mock_exit:
            send_request("GET", "http://example.com")
            mock_exit.assert_called_once_with(1)

    @patch("http_tool.request.urlopen")
    def test_url_error(self, mock_urlopen):
        from urllib.error import URLError
        
        mock_urlopen.side_effect = URLError("Connection refused")
        
        with patch("sys.exit") as mock_exit:
            send_request("GET", "http://example.com")
            mock_exit.assert_called_once_with(1)


class TestIntegration:
    @patch("http_tool.request.urlopen")
    def test_full_request_response_cycle(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "success": True,
            "data": {"id": 1, "name": "test"}
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        with patch("sys.argv", ["http_tool.py", "GET", "http://example.com/api"]):
            from http_tool import main
            main()
        
        mock_urlopen.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
