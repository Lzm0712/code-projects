"""pytest 配置和 fixture"""
import pytest
import asyncio
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环 fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """同步测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_weather_service():
    """模拟天气服务"""
    mock = AsyncMock()
    mock.get_weather.return_value = {
        "code": "200",
        "updateTime": "2024-01-01T12:00:00+08:00",
        "location": {
            "name": "北京",
            "country": "中国"
        },
        "now": {
            "temp": "15",
            "text": "多云",
            "humidity": "45",
            "windSpeed": "12",
            "feelsLike": "13",
            "pressure": "1015",
            "vis": "10"
        }
    }
    return mock
