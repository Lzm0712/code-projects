# Python HTTP Server

一个轻量级的 Python HTTP 服务器实现，支持基本的路由功能。

## 项目介绍

本项目是一个基于 Python 标准库 `http.server` 的简单 HTTP 服务器，提供了常见的 RESTful 风格接口支持。

### 功能特性

- 轻量级，无需额外依赖
- 支持 GET/POST 请求
- 内置路由系统
- 支持查询参数
- 返回 JSON/HTML/纯文本多种格式

## 快速开始

### 环境要求

- Python 3.6+

### 安装

```bash
# 克隆项目
cd /Users/liuzimin/http-server-demo

# 直接运行（无需安装）
python3 server.py
```

### 启动服务器

```bash
# 默认配置（localhost:8080）
python3 server.py

# 自定义主机和端口
python3 server.py --host 0.0.0.0 --port 3000
```

服务器启动后，访问 `http://localhost:8080/`

## API 说明

### GET 接口

| 路由 | 描述 | 示例 |
|------|------|------|
| `GET /` | 首页，返回 HTML 页面 | `curl http://localhost:8080/` |
| `GET /hello` | 返回问候信息 | `curl http://localhost:8080/hello` |
| `GET /hello?name=Alice` | 带参数的问候 | `curl "http://localhost:8080/hello?name=Alice"` |
| `GET /time` | 返回服务器当前时间 | `curl http://localhost:8080/time` |
| `GET /json` | 返回 JSON 格式数据 | `curl http://localhost:8080/json` |
| `GET /headers` | 返回请求头信息 | `curl http://localhost:8080/headers` |

### POST 接口

| 路由 | 描述 | 示例 |
|------|------|------|
| `POST /echo` | 回显 POST body 内容 | `curl -X POST -d "hello" http://localhost:8080/echo` |

## 示例

### 1. 访问首页

```bash
$ curl http://localhost:8080/
<!DOCTYPE html>
<html>
<head><title>Python HTTP Server</title></head>
<body>
    <h1>Welcome to Python HTTP Server</h1>
    ...
</body>
</html>
```

### 2. 获取问候

```bash
$ curl http://localhost:8080/hello
Hello, World!

$ curl "http://localhost:8080/hello?name=Alice"
Hello, Alice!
```

### 3. 获取 JSON 数据

```bash
$ curl http://localhost:8080/json
{
  "status": "success",
  "message": "This is a JSON response",
  "data": {
    "version": "1.0.0",
    "timestamp": "2026-06-24T12:00:00.000000"
  }
}
```

### 4. 获取服务器时间

```bash
$ curl http://localhost:8080/time
Server time: 2026-06-24 12:00:00
```

### 5. POST 请求

```bash
$ curl -X POST -d "Hello Server" http://localhost:8080/echo
Received: Hello Server
```

## 测试方法

### 手动测试

使用 curl 测试各个接口：

```bash
# GET 请求测试
curl http://localhost:8080/
curl http://localhost:8080/hello
curl "http://localhost:8080/hello?name=Test"
curl http://localhost:8080/time
curl http://localhost:8080/json
curl http://localhost:8080/headers

# POST 请求测试
curl -X POST -d "test data" http://localhost:8080/echo
```

### 自动化测试

创建测试脚本 `test_server.py`：

```python
import unittest
import json
from server import HTTPRequestHandler
from http.server import HTTPServer
import threading
import time
import urllib.request

class TestHTTPHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('localhost', 8765), HTTPRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()
        cls.base_url = 'http://localhost:8765'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_index(self):
        response = urllib.request.urlopen(f'{self.base_url}/')
        self.assertEqual(response.status, 200)

    def test_hello_default(self):
        response = urllib.request.urlopen(f'{self.base_url}/hello')
        self.assertEqual(response.status, 200)
        self.assertIn(b'Hello', response.read())

    def test_hello_with_name(self):
        response = urllib.request.urlopen(f'{self.base_url}/hello?name=Alice')
        self.assertEqual(response.status, 200)
        self.assertIn(b'Alice', response.read())

    def test_json(self):
        response = urllib.request.urlopen(f'{self.base_url}/json')
        data = json.loads(response.read())
        self.assertEqual(data['status'], 'success')

    def test_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(f'{self.base_url}/nonexistent')
        self.assertEqual(ctx.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
```

运行测试：

```bash
python3 -m unittest test_server.py -v
```

## 项目结构

```
http-server-demo/
├── README.md          # 本文档
└── server.py          # 服务器主程序
```

## 许可证

MIT License
