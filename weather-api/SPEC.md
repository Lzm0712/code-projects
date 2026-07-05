# 天气查询 API 服务 — 规格说明书

## 1. 项目概述

- **项目名称**：weather-api
- **项目类型**：REST API 天气查询服务
- **核心功能**：提供城市天气数据查询接口，基于城市名返回实时天气信息
- **目标用户**：中国用户群体，需要精准国内天气数据

## 2. 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 原生异步支持、Pydantic 自动校验、自动文档 |
| HTTP 客户端 | httpx | 异步 HTTP 调用 |
| 天气数据源 | 和风天气 (Qweather) | 中国数据最优，免费额度 1000次/天 |
| 测试框架 | pytest | 单元测试与集成测试 |

> **约束**：不许改变技术选型，有问题上报 Coordinator

## 3. 接口规格

### 3.1 天气查询

- **端点**：`GET /weather`
- **查询参数**：
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | city | string | 是 | 城市名称（中文或英文） |
- **成功响应**（200）：
```json
{
  "city": "北京",
  "country": "中国",
  "temp": "15",
  "text": "多云",
  "humidity": "45",
  "wind_speed": "12",
  "feels_like": "13",
  "pressure": "1015",
  "vis": "10",
  "update_time": "2024-01-01 12:00"
}
```
- **错误响应**：
  - 400：缺少或无效 city 参数
  - 404：城市未找到
  - 429：API 请求次数超限
  - 500：服务器内部错误
  - 502：天气 API 调用失败

### 3.2 健康检查

- **端点**：`GET /health`
- **成功响应**（200）：
```json
{
  "status": "healthy",
  "service": "weather-api"
}
```

## 4. 项目结构

```
weather-api/
├── SPEC.md
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 应用入口
│   ├── config.py        # 配置管理
│   ├── routers/
│   │   ├── __init__.py
│   │   └── weather.py   # 天气路由
│   ├── services/
│   │   ├── __init__.py
│   │   └── weather.py   # 和风天气 API 调用
│   └── models/
│       ├── __init__.py
│       └── weather.py   # Pydantic 响应模型
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_weather.py  # 天气接口测试
```

## 5. 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| QWEATHER_API_KEY | 是 | 和风天气 API Key |

## 6. 依赖列表

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
httpx>=0.24.0
pydantic>=2.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

## 7. 验收标准

- [ ] 启动服务：`uvicorn app.main:app --host 0.0.0.0 --port 8080`
- [ ] 文档访问：`http://localhost:8080/docs`（Swagger UI）
- [ ] 健康检查：`GET /health` 返回 200
- [ ] 天气查询：`GET /weather?city=北京` 返回实时天气数据
- [ ] 参数校验：缺少 city 参数返回 400
- [ ] 错误处理：无效城市返回 404
- [ ] 异步实现：所有外部 API 调用使用 async/await
- [ ] 类型安全：Pydantic 模型自动校验请求与响应
- [ ] 测试通过：pytest 单元测试全部通过

## 8. 已知限制

- 和风天气免费套餐限制：每天 1000 次请求
- 免费套餐仅提供基础 3 天预报
- 小时级预报需付费套餐支持
