"""和风天气 API 服务"""
import httpx
from typing import Dict, Any

from app.config import get_config


class WeatherService:
    """和风天气服务"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.qweather_base_url
        self.api_key = self.config.qweather_api_key
    
    async def get_weather(self, city: str) -> Dict[str, Any]:
        """
        获取城市实时天气
        
        Args:
            city: 城市名称
            
        Returns:
            天气数据字典
            
        Raises:
            httpx.HTTPStatusError: API 请求失败时
        """
        params = {
            "location": city,
            "key": self.api_key,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != "200":
                raise ValueError(f"Weather API error: {data.get('code')}")
            
            return data


def get_weather_service() -> WeatherService:
    """获取天气服务实例"""
    return WeatherService()
