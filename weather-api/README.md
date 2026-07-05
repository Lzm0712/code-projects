# Weather API

基于 FastAPI + 和风天气 的城市天气查询 REST API 服务。

## 技术栈

- **框架**：FastAPI
- **HTTP 客户端**：httpx
- **天气数据源**：和风天气 (Qweather)
- **测试**：pytest

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
export QWEATHER_API_KEY=your_api_key_here
```

获取和风天气 API Key：https://dev.qweather.com/

### 3. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 4. 访问文档

- Swagger UI：http://localhost:8080/docs
- ReDoc：http://localhost:8080/redoc

## API 接口

### 天气查询

```
GET /weather?city=城市名
```

**示例请求**：

```bash
curl "http://localhost:8080/weather?city=北京"
```

**成功响应**（200）：

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

**错误响应**：

| 状态码 | 说明 |
|--------|------|
| 400 | 缺少或无效 city 参数 |
| 404 | 城市未找到 |
| 429 | API 请求次数超限 |
| 500 | 服务器内部错误 |
| 502 | 天气 API 调用失败 |

### 健康检查

```
GET /health
```

**成功响应**（200）：

```json
{
  "status": "healthy",
  "service": "weather-api"
}
```

## 项目结构

```
weather-api/
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
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_weather.py  # 天气接口测试
├── requirements.txt
├── SPEC.md
└── README.md
```

## 运行测试

```bash
pytest -v
```

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| QWEATHER_API_KEY | 是 | 和风天气 API Key |

## 和风天气免费套餐限制

- 每天 1000 次请求
- 基础 3 天预报
- 小时级预报需付费套餐

## 参考链接

- 和风天气文档：https://dev.qweather.com/
- FastAPI 文档：https://fastapi.tiangolo.com/
