# ECC Loop — 5-Stage 重构计划

## 目标
将 ECC Loop 从三个散件，重构为真正的**五阶段闭环引擎**。

## 当前问题
- `seed.py` → 只能读写状态，无 DISCOVER 能力
- `reflection.py` → 纯分析，无 PLAN 分解
- `scanner.py` → 单向扫描，无 ITERATE 回退
- 三个模块没有统一调度，无 VERIFY，无 EXECUTE

---

## 新五阶段架构

```
DISCOVER ──→ PLAN ──→ EXECUTE ──→ VERIFY ──→ ITERATE
    ↑                                            │
    └──────────────── FAIL ──────────────────────┘
```

### Stage 1: DISCOVER（发现问题）
**目标**：从 observations、skills、seed 中提取当前状态和待解决问题。

- 读取 `~/.hermes/observations.jsonl`（最近的交互记录）
- 对比 `seed.json`（当前已知状态）
- 输出：`DiscoveryResult{issue, context, goals}`

### Stage 2: PLAN（任务规划）
**目标**：将问题拆解为可执行任务序列。

- 分析 DiscoveryResult
- 生成有序任务列表（task_1 → task_2 → ...）
- 评估每个任务的复杂度（简单/复杂）
- 输出：`Plan{tasks: [{name, complexity, status}]}`

### Stage 3: EXECUTE（执行）
**目标**：按计划执行任务，记录结果。

- 遍历 Plan.tasks
- 每个任务调用对应 handler（skill、code、shell）
- 收集执行输出和错误
- 输出：`ExecutionResult{task_name, output, error, status}`

### Stage 4: VERIFY（验证）
**目标**：对照 PLAN 目标，验证 EXECUTE 结果。

- 检查每个任务的 status（成功/失败）
- 如果有 FAIL → 触发 ITERATE
- 如果全部 PASS → 输出最终结果，标记 seed 完成
- 输出：`VerifyResult{passed, failed_tasks, summary}`

### Stage 5: ITERATE（迭代）
**目标**：失败时回到 DISCOVER，带上前面的反馈。

- 接收 VerifyResult（包含失败原因）
- 更新 seed.state（记录失败点）
- 将反馈注入新的 DISCOVER 输入
- 形成新的 DISCOVER → PLAN → ... 循环

---

## 文件结构（重构后）

```
ecc_loop/
├── __init__.py
├── seed.py          # 保留，净化为纯状态管理
├── scanner.py       # 保留，净化为 skill 检测
├── reflection.py     # 保留，净化为单一分析逻辑
│
├── engine.py         # 新增：五阶段闭环调度器
│   ├── discover()   # Stage 1
│   ├── plan()       # Stage 2
│   ├── execute()    # Stage 3
│   ├── verify()     # Stage 4
│   └── iterate()    # Stage 5
│
├── models.py         # 新增：数据结构（DiscoveryResult, Plan, etc.）
├── handlers.py       # 新增：EXECUTE 阶段的任务处理器
└── cli.py            # 新增：命令行入口（hermes ecc run）
```

## 重构优先级

### Phase 1（核心引擎）
1. `models.py` — 定义所有数据结构
2. `engine.py` — 五阶段调度器（不含具体 handler 实现）
3. 修改 `seed.py` — 移除冗余逻辑，只保留状态读写
4. `cli.py` — `hermes ecc run <goal>` 入口

### Phase 2（执行能力）
5. `handlers.py` — Skill handler、Code handler、Shell handler
6. 修改 `reflection.py` — 作为 DISCOVER 的分析引擎

### Phase 3（完善闭环）
7. 修改 `scanner.py` — 作为 ITERATE 的触发器之一
8. 写 `tests/test_engine.py`
9. 更新 `pyproject.toml` + `README.md`

## 成功标准
- `hermes ecc run "分析我最近的工作模式"` 能完整走完五个阶段
- `verify` 失败时能正确回退到 `discover`
- 所有模块有单元测试
