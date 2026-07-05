"""天气接口测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app


class TestHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_check_returns_200(self, client: TestClient):
        """测试健康检查返回 200"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_response_format(self, client: TestClient):
        """测试健康检查响应格式"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "weather-api"


class TestWeatherEndpoint:
    """天气查询端点测试"""
    
    def test_weather_without_city_returns_400(self, client: TestClient):
        """测试缺少 city 参数返回 400"""
        response = client.get("/weather")
        assert response.status_code == 422  # FastAPI validation error
    
    def test_weather_with_empty_city_returns_400(self, client: TestClient):
        """测试空 city 参数返回 400"""
        response = client.get("/weather?city=")
        assert response.status_code == 422
    
    @patch("app.routers.weather.get_weather_service")
    def test_weather_returns_200(self, mock_get_service, client: TestClient):
        """测试有效城市查询返回 200"""
        mock_service = AsyncMock()
        mock_service.get_weather.return_value = {
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
        mock_get_service.return_value = mock_service
        
        response = client.get("/weather?city=北京")
        assert response.status_code == 200
    
    @patch("app.routers.weather.get_weather_service")
    def test_weather_response_format(self, mock_get_service, client: TestClient):
        """测试天气响应格式正确"""
        mock_service = AsyncMock()
        mock_service.get_weather.return_value = {
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
        mock_get_service.return_value = mock_service
        
        response = client.get("/weather?city=北京")
        data = response.json()
        
        assert "city" in data
        assert "country" in data
        assert "temp" in data
        assert "text" in data
        assert "humidity" in data
        assert "wind_speed" in data
        assert "feels_like" in data
        assert "pressure" in data
        assert "vis" in data
        assert "update_time" in data
    
    @patch("app.routers.weather.get_weather_service")
    def test_weather_city_not_found_returns_404(self, mock_get_service, client: TestClient):
        """测试无效城市返回 404"""
        import httpx
        mock_service = AsyncMock()
        mock_service.get_weather.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=404)
        )
        mock_get_service.return_value = mock_service
        
        response = client.get("/weather?city=无效城市名")
        assert response.status_code == 404
    
    @patch("app.routers.weather.get_weather_service")
    def test_weather_rate_limit_returns_429(self, mock_get_service, client: TestClient):
        """测试 API 超限返回 429"""
        import httpx
        mock_service = AsyncMock()
        mock_service.get_weather.side_effect = httpx.HTTPStatusError(
            "Rate Limit",
            request=MagicMock(),
            response=MagicMock(status_code=429)
        )
        mock_get_service.return_value = mock_service
        
        response = client.get("/weather?city=北京")
        assert response.status_code == 429
    
    @patch("app.routers.weather.get_weather_service")
    def test_weather_api_error_returns_502(self, mock_get_service, client: TestClient):
        """测试天气 API 错误返回 502"""
        import httpx
        mock_service = AsyncMock()
        mock_service.get_weather.side_effect = httpx.HTTPStatusError(
            "Bad Gateway",
            request=MagicMock(),
            response=MagicMock(status_code=502)
        )
        mock_get_service.return_value = mock_service
        
        response = client.get("/weather?city=北京")
        assert response.status_code == 502
