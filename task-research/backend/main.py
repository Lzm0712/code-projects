"""
FastAPI Demo Application
基于技术选型调研结论（FastAPI 胜出）实现的 REST API 演示项目
"""
from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Demo",
    description="基于技术选型调研结论实现的 FastAPI 演示项目",
    version="1.0.0",
)


@app.get("/")
async def root():
    """根路径，返回欢迎信息"""
    return {"message": "Welcome to FastAPI Demo", "status": "ok"}


@app.get("/hello")
async def hello(name: str = "World"):
    """问候接口，支持自定义名称"""
    return {"message": f"Hello, {name}!", "status": "ok"}
