"""FastAPI 应用入口"""
from fastapi import FastAPI

from app.models.weather import HealthResponse
from app.routers.weather import router as weather_router

app = FastAPI(
    title="Weather API",
    description="天气查询 REST API 服务",
    version="1.0.0"
)

# 注册路由
app.include_router(weather_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    健康检查接口
    
    Returns:
        服务健康状态
    """
    return HealthResponse(status="healthy", service="weather-api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
