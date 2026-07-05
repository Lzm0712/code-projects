# ECC Loop — 完整架构文档

## 架构全景

```
                    ┌── discover_work() ───────────────────────┐
                    │  git status / TODO commits /             │
                    │  pytest cache / stale branches            │
                    └────────────────┬─────────────────────────┘
                                     ↓
  ┌──────────────────────────────────────────────────────────────────┐
  │                        ECC LOOP ENGINE                            │
  │                                                                  │
  │  DISCOVER ──→ PLAN ──→ EXECUTE ──→ VERIFY(5层) ──→ ITERATE      │
  │     ↑                                                  │         │
  │     └──────────── FAIL (feedback) ─────────────────────┘         │
  │                                                                  │
  │  Circuit Breaker │ goal_freeze │ safety guard │ cycle log        │
  └──────────────────────────────────────────────────────────────────┘
                                     ↓
  ┌──────────────────────────────────────────────────────────────────┐
  │                     ECC 命令层 (CLI)                              │
  │  run │ loop │ goal │ fix │ evolve │ improve │ scan │ status      │
  └──────────────────────────────────────────────────────────────────┘
```

## 模块清单（16 个）

| 模块 | 行数 | 职责 | 来源 |
|------|------|------|------|
| `engine.py` | 728 | 五阶段调度器 + circuit breaker + verifier | 核心 |
| `models.py` | 142 | 数据结构 + CircuitBreakerConfig | 核心 |
| `handlers.py` | 103 | Shell/Code/File handler + 自动检测 | 核心 |
| `seed.py` | 110 | 状态持久化 + 定期清理 | 核心 |
| `scanner.py` | 91 | Skill 变更检测 | 核心 |
| `reflection.py` | 98 | Observations 分析 + 分层反思 | 核心 |
| `cli.py` | 266 | CLI 入口 (run/loop/goal/fix/evolve/improve) | 核心 |
| `logger.py` | 19 | 循环日志 (.ecc_logs/) | Best Practice #4 |
| `goal_freeze.py` | 37 | 目标冻结（防 mid-loop drift） | Best Practice #2 |
| `precise_specs.py` | 53 | 二元成功标准 (Spec/Specs) | Best Practice #5 |
| `worktree.py` | 79 | 文件级沙箱隔离 | Best Practice #6 |
| `learning.py` | 77 | 循环指标 + 趋势分析 | Best Practice #8 |
| `llm.py` | 140 | DeepSeek LLM 集成 (generate_fix + LLMHandler) | LLM |
| `run_log.py` | 55 | 结构化 JSONL 运行日志 | operating-loops |
| `safety.py` | 43 | denylist + human gates | safety.md |
| `reader.py` | 66 | 读取 diff/日志/进度 构建上下文 | opencode-loop |
| `checkpoint.py` | 70 | progress.md 进度追踪 | opencode-loop |
| `continual.py` | 70 | 从运行中提取模式 | everything-claude-code |

## 五阶段 Pipeline

```
Stage 1: DISCOVER
  ├── _discover_gaps()     → 文件缺口 / 未使用import / 配置校验
  ├── discover_work()      → git状态 / TODO/FIXME / pytest缓存
  └── reflection.analyze() → observations 分析

Stage 2: PLAN
  ├── _extract_goals()     → 代码块不拆分
  └── goal_freeze.freeze() → 锁定目标规格

Stage 3: EXECUTE
  ├── safety_check()       → denylist拦截 + human gate
  ├── handler_for()        → Shell/Code/File/LLM 自动检测
  └── WorktreeHandler      → 隔离执行

Stage 4: VERIFY (5层)
  ├── verify()             → 内部任务状态
  ├── run_verifier()       → pytest
  ├── run_typecheck()      → mypy
  ├── Specs.verify()       → 二元成功标准
  └── run_reviewer()       → LLM审查 (default: REJECT)

Stage 5: ITERATE
  ├── feedback注入DISCOVER
  ├── circuit_breaker检测
  └── continual.extract() → 学习模式
```

## VERIFY 管线（5 层防御）

```
EXECUTE
  ↓
[1] 内部 verify()      — 任务是否抛异常
  ↓ PASS
[2] pytest             — 73 tests
  ↓ PASS
[3] mypy typecheck     — 类型检查
  ↓ PASS
[4] Specs.verify()     — 二元成功标准
  ↓ PASS
[5] LLM reviewer       — 独立审查 (default: REJECT)
  ↓ PASS
✅ 交付
```

## Loop Engineering 对标

### 8 项最佳实践：8/8 ✅

| # | 实践 | ECC实现 |
|---|------|---------|
| 1 | 从简单开始 | run → loop → goal 渐进 |
| 2 | 保持规格不变 | goal_freeze.py |
| 3 | 投资于技能 | LOOP.md + scanner |
| 4 | 记录一切 | logger + run_log + continual |
| 5 | 编写精确规格 | precise_specs.py |
| 6 | 工作树隔离 | worktree.py |
| 7 | 分层验证 | 5-layer verify pipeline |
| 8 | 保持学习 | learning + continual |

### 6 大组件

| 组件 | ECC | 对应 |
|------|-----|------|
| Automations | ✅ | Hermes cron (每1h巡检+每日9点日报) |
| Worktrees | ✅ | WorktreeHandler |
| Skills | ✅ | scanner + LOOP.md |
| Plugins | ⚠️ | 文件系统 + LLM (待MCP) |
| Sub-agents | ✅ | LLM reviewer (separate model) |
| Memory | ✅ | seed.json + logger + run_log |

### 反模式修复

| 反模式 | 修复 |
|--------|------|
| Same agent implements and verifies | LLM reviewer (separate model, REJECT default) |
| No attempt cap | Circuit breaker (max_iterations + consecutive_failures) |
| No kill switch | loop-budget.md + pause criteria |
| State rot | seed.json auto-pruning |
| Verifier theater | 5-layer pipeline + spec checks |

## 安全防护

```
safety.py:
  Denylist: .env, secrets, credentials, keys, migrations, auth, payments
  Human gates: >10 files, dependency changes, 3rd retry
  loop-constraints.md: machine-readable rules
```

## 学习系统

```
continual.py:
  extract_patterns() → 从 run-log 提取重复错误模式
  save_learned()     → 保存到 learned-patterns.json

learning.py:
  record()           → 记录每次循环的指标
  summary()          → 总运行数/通过率/趋势分析
  _trend()           → improving / stable / degrading
```

## 数据流

```
seed.json       ← 状态持久化
.ecc_logs/
  ecc-YYYYMMDD.log  ← 循环日志
  run-log.jsonl     ← 结构化运行记录
  metrics.json      ← 学习指标
  learned-patterns.json ← 持续学习输出
LOOP.md         ← 声明式配置
loop-constraints.md ← 安全约束
loop-budget.md  ← 预算文档
```

## 测试矩阵

```
20 test files / 73 tests / 2 skipped (API-dependent)

test_engine, test_models, test_cli, test_seed, test_scanner
test_handlers, test_reflection, test_circuit_breaker
test_integration, test_goal, test_config_validation
test_llm, test_logger, test_goal_freeze, test_precise_specs
test_worktree, test_learning, test_safety, test_self_evolution
test_run_log (todo)
```

## 与 Hermes 原生集成

| Hermes 能力 | ECC 当前 | 建议 |
|------------|---------|------|
| `hermes cron` | 任务驱动 | 可选定时触发 |
| `delegate_task` | subprocess | 换用 native delegation |
| `hermes memory` | seed.json | 可双向同步 |
| `hermes mcp` | 无 | 接入外部工具 |
