"""
FastAPI Demo 单元测试
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """测试根路径 /"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI Demo", "status": "ok"}


def test_hello_default():
    """测试 /hello 默认参数"""
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!", "status": "ok"}


def test_hello_custom_name():
    """测试 /hello 自定义名称"""
    response = client.get("/hello?name=FastAPI")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!", "status": "ok"}
