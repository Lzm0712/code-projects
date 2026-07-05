# Mem0 本地部署 STATE

**日期**: 2026-06-21
**状态**: 🚧 执行中

---

## 目标

本地部署 mem0（不依赖云服务），集成到 Hermes Agent

---

## Plan

### Phase 1: 安装
- [ ] pip install mem0ai
- [ ] pip install qdrant-client (向量数据库客户端)
- [ ] 启动 Qdrant (Docker 或本地)

### Phase 2: 配置
- [ ] 配置 mem0 使用 Qdrant 本地实例
- [ ] 设置 .env

### Phase 3: 测试
- [ ] 写入一条记忆
- [ ] 查询记忆
- [ ] 验证跨 session 持久化

### Phase 4: 集成 Hermes
- [ ] 创建 mem0 MCP 工具或 skill
- [ ] 验证在 Hermes 中可用

---

## 回滚点

无（首次部署）

---

## 实施记录

