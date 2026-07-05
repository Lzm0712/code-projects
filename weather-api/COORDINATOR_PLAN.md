# Coordinator 任务拆分

## 原始需求
实现一个 REST API 天气查询服务

## 任务拆分

### Researcher 任务
- 调研天气 API 方案（免费/付费对比）
- 评估 Python Web 框架选型（FastAPI vs Flask）
- 给出置信度评分

### Writer 任务
- 基于 Researcher 结论写 SPEC.md
- 基于 SPEC 写 README.md
- **注意：不许改技术选型结论，有问题报 Coordinator**

### Builder 任务
- 严格按 SPEC.md 实现
- 自检清单：功能完整性、边界处理、测试覆盖
- 交付前必须自测通过

## 规格要求（Coordinator 制定，Writer/Builder 不许改）
- 框架：FastAPI
- 端口：8080
- 端点：GET /weather?city=城市名
- 依赖：httpx（调用天气 API）
- 测试：pytest
- **不许改变接口和框架选择**
