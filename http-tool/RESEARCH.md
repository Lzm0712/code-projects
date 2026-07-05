# Python HTTP 请求方案调研报告

## 1. 概述

Python 生态中主流 HTTP 请求库有三个：**urllib**（标准库）、**requests**（第三方）、**httpx**（第三方）。

---

## 2. urllib（标准库）

- **模块**: `urllib.request`, `urllib.parse`, `urllib.error`
- **同步**: ✅ 原生同步
- **异步**: ❌ 无（需配合 `asyncio` + `aiohttp`）
- **依赖**: 无（标准库）
- **API 风格**: 繁琐，流程：`Request → urlopen → Response`
- **功能**: 基本 GET/POST、基础 auth、URL 参数编码
- **生态**: 内置，无外部依赖
- **版本**: Python 3.x 内置

**置信度**: 9/10（标准库，特性稳定，广泛文档）

---

## 3. requests

- **作者**: Kenneth Reitz（2011）
- **同步**: ✅ 原生同步
- **异步**: ❌ 需配合 `requests-futures` / `grequests`
- **依赖**: `urllib3`, `charset-normalizer`, `idna`, `certifi`
- **API 风格**: 简洁直观，`requests.get(url)`, `requests.post(url, json=...)`
- **功能**: Session/Cookie、连接池、自动解码、文件上传下载、基础/摘要认证、超时控制、重定向控制
- **生态**: 超大规模（star 最多的 Python 库之一），文档丰富
- **版本**: 2.x（当前稳定）

**置信度**: 9/10（业界标准，10+年生产验证）

---

## 4. httpx

- **作者**: encode 团队（2019）
- **同步**: ✅ 原生同步
- **异步**: ✅ 原生 async/await 支持
- **依赖**: `httpcore`, `anyio`, `certifi`, `h11`/`h2`（HTTP/2）
- **API 风格**: requests 兼容设计，`httpx.get(url)` / `async with httpx.AsyncClient() as client: await client.get(url)`
- **功能**: HTTP/1.1 + HTTP/2、连接池、Streaming、Async、Mock 支持、请求/响应拦截器
- **生态**: 快速增长，FastAPI/Starlette 生态深度集成
- **版本**: 0.x → 1.x（2024稳定）

**置信度**: 8/10（现代首选，但相对年轻）

---

## 5. 对比矩阵

| 维度 | urllib | requests | httpx |
|------|--------|----------|-------|
| 同步 | ✅ | ✅ | ✅ |
| 异步 | ❌ | ❌ | ✅ |
| HTTP/2 | ❌ | ❌ | ✅ |
| 标准库 | ✅ | ❌ | ❌ |
| API 简洁度 | 低 | 高 | 高 |
| 连接池 | 基础 | ✅ | ✅ |
| 超时控制 | 基础 | ✅ | ✅ |
| 流式响应 | 基础 | ✅ | ✅ |
| 拦截器 | ❌ | ❌ | ✅ |
| Starlette/FastAPI 集成 | ❌ | 需适配 | ✅ 原生 |

---

## 6. 选型建议

| 场景 | 推荐 |
|------|------|
| 简单脚本、快速验证 | **requests** |
| 需要 async + HTTP/2 | **httpx** |
| 避免外部依赖 | **urllib** |
| FastAPI/Starlette 后端 | **httpx** |
| 生产级稳定项目 | **requests**（久经考验）|

---

## 7. 置信度总结

| 库 | 置信度 |
|----|--------|
| urllib | 9/10 |
| requests | 9/10 |
| httpx | 8/10 |

---

## 8. 参考资料

- Python 官方文档: https://docs.python.org/3/library/urllib.html
- requests: https://requests.readthedocs.io/
- httpx: https://www.python-httpx.org/
- GitHub stars（参考）: requests ~50k, httpx ~14k（截至2024）
