# FastAPI Demo

基于技术选型调研结论实现的 FastAPI 演示项目。

## 技术选型依据

参考 [TECH_SELECTION.md](../../TECH_SELECTION.md)，FastAPI 以 8.2 分综合加权得分胜出。

## 快速开始

```bash
# 安装依赖
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 运行测试
pytest -v

# 启动服务
uvicorn main:app --reload
```

## API 端点

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 欢迎信息 |
| `/hello` | GET | 问候接口，支持 `name` 参数 |

## 示例

```bash
# 获取欢迎信息
curl http://localhost:8000/

# 自定义问候
curl http://localhost:8000/hello?name=FastAPI
```

启动后访问 http://localhost:8000/docs 查看自动生成的 OpenAPI 文档。
