# ECC Loop — Evolutionary Consciousness Code Loop

Hermes Agent 自改进循环。通过研究外部框架（如 JiuwenSwarm），提炼可落地的设计模式，持续优化 Hermes 的自进化能力。

## 架构

```
ecc-loop/
├── ecc_loop/           # 核心模块
│   ├── seed.py         # STATE.md ↔ seed.json 序列化
│   ├── reflection.py   # 分层复盘（快/慢路径）
│   └── scanner.py      # Skill 热更新扫描
├── plans/              # 研究 & 实施计划
├── research/           # 研究成果
└── tests/              # 测试
```

## 三个改进方向

| # | 改进 | 来源 | 状态 |
|---|------|------|------|
| A | build_context_seed 序列化 | JiuwenSwarm `to_seed()`/`from_seed()` | ✅ 完成 |
| B | Skill 热更新机制 | JiuwenSwarm `update_evolution_config()` | ✅ 完成 |
| C | 分层复盘 (FastOneShotPlanner) | JiuwenSwarm 贪心 vs BFS 规划 | ✅ 完成 |
