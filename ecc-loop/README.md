# ECC Loop

**Evolutionary Consciousness Code Loop** — Hermes Agent 自改进引擎。

五阶段闭环：DISCOVER → PLAN → EXECUTE → VERIFY → ITERATE
对标 [loop-engineering](https://github.com/cobusgreyling/loop-engineering) 框架。

## 快速开始

```bash
cd ~/projects/ecc-loop
uv run ecc status         # 查看当前状态
uv run ecc run "goal"     # 单次执行
uv run ecc loop "goal"    # 完整闭环（FAIL 自动迭代直到 PASS 或熔断）
```

## 架构

```
ecc_loop/
├── models.py      # 数据结构 + CircuitBreaker
├── engine.py      # 五阶段调度器 (run_one / loop)
├── handlers.py    # Shell/Skill/Code 任务处理器
├── seed.py        # 状态持久化 (seed.json)
├── reflection.py  # Observations 分析引擎
├── scanner.py     # Skill 变更检测
└── cli.py         # 命令行入口

LOOP.md            # 声明式循环配置
STATE.md           # 人工可读项目状态
```

## 五阶段

```
DISCOVER ──→ PLAN ──→ EXECUTE ──→ VERIFY
    ↑                               │
    └─────────── FAIL ──────────────┘ (feedback 注入 DISCOVER)
```

| 阶段 | Karpathy 原则 | 做什么 |
|------|--------------|--------|
| DISCOVER | Think Before Coding | 收集上下文、暴露假设、接收反馈 |
| PLAN | Simplicity First | 最小任务分解 |
| EXECUTE | Surgical Changes | 只执行 PLAN 定义的任务 |
| VERIFY | Goal-Driven | PASS → 交付，FAIL → 带反馈回 DISCOVER |

## 测试

```bash
uv run pytest
# 39 tests, 全部通过
```
