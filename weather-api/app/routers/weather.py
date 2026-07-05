"""天气路由"""
from fastapi import APIRouter, Query, HTTPException, status
import httpx

from app.models.weather import WeatherResponse
from app.services.weather import get_weather_service

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherResponse)
async def get_weather(
    city: str = Query(..., min_length=1, description="城市名称（中文或英文）")
) -> WeatherResponse:
    """
    查询城市天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气响应数据
        
    Raises:
        HTTPException: 各种错误状态码
    """
    if not city or not city.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少或无效 city 参数"
        )
    
    service = get_weather_service()
    
    try:
        data = await service.get_weather(city.strip())
        weather_data = data.get("now", {})
        location_data = data.get("location", {})
        
        # 格式化更新时间
        update_time = data.get("updateTime", "")
        if update_time:
            # 格式: 2024-01-01 12:00
            update_time = update_time.replace("T", " ").replace("+08:00", "")
        
        return WeatherResponse(
            city=location_data.get("name", city),
            country=location_data.get("country", "中国"),
            temp=weather_data.get("temp", ""),
            text=weather_data.get("text", ""),
            humidity=weather_data.get("humidity", ""),
            wind_speed=weather_data.get("windSpeed", ""),
            feels_like=weather_data.get("feelsLike", ""),
            pressure=weather_data.get("pressure", ""),
            vis=weather_data.get("vis", ""),
            update_time=update_time
        )
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API 请求次数超限"
            )
        elif e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="城市未找到"
            )
        elif e.response.status_code >= 500:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="天气 API 调用失败"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"城市未找到: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        )
