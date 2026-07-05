"""天气数据 Pydantic 模型"""
from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    """天气响应模型"""
    city: str = Field(..., description="城市名称")
    country: str = Field(..., description="国家")
    temp: str = Field(..., description="温度（摄氏度）")
    text: str = Field(..., description="天气文字描述")
    humidity: str = Field(..., description="相对湿度（%）")
    wind_speed: str = Field(..., description="风速（公里/小时）")
    feels_like: str = Field(..., description="体感温度（摄氏度）")
    pressure: str = Field(..., description="气压（hPa）")
    vis: str = Field(..., description="能见度（公里）")
    update_time: str = Field(..., description="数据更新时间")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(default="healthy")
    service: str = Field(default="weather-api")
