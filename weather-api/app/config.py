"""配置管理"""
import os
from functools import lru_cache


class Config:
    """应用配置"""
    
    def __init__(self):
        self.qweather_api_key: str = os.getenv("QWEATHER_API_KEY", "")
        self.qweather_base_url: str = "https://devapi.qweather.com/v7/weather/now"
    
    def validate(self) -> None:
        """验证配置"""
        if not self.qweather_api_key:
            raise ValueError("QWEATHER_API_KEY environment variable is required")


@lru_cache()
def get_config() -> Config:
    """获取配置单例"""
    config = Config()
    config.validate()
    return config
