# JiuwenSwarm 研究 → ECC Loop 实施计划

**Goal:** 将 JiuwenSwarm 三个最佳实践落地到 ECC Loop
**Loop Engineering 模式:** 每任务完成后更新 STATE.md，失败立即回滚

---

## 三个改进方向（来自 JiuwenSwarm）

### A. build_context_seed 可序列化设计
**来源:** assembly.py 的 `to_seed()` / `from_seed()` 双轨机制
**ECC 现状:** STATE.md 是纯文本，无结构化序列化
**改进:** 引入 `build_seed.json` 结构化快照，支持跨进程重建

### B. 热更新机制
**来源:** TeamManager 的 `update_evolution_config()` 运行时热更新 Rails
**ECC 现状:** skill 加载后不热重载，重启 gateway 才生效
**改进:** cron job 触发 skill 重扫描，动态更新 skill 加载状态

### C. FastOneShotPlanner 分层规划
**来源:** FastOneShotPlanner（≤40 skills 贪心）vs BFS（复杂多步）
**ECC 现状:** 每次复盘都全量执行，不分层
**改进:** 两级复盘——简单 query 直接输出，复杂 query 走完整规划

---

## 任务分解

### Task A1: 分析现有 STATE.md 序列化结构

**Objective:** 理解当前 STATE.md 的字段结构

**Files:**
- Read: `~/ecc-loop/STATE.md`

**Step 1: 读 STATE.md**
- 统计字段数量、类型、使用频率
- 找出缺失字段（无版本号、无序列化时间戳）

**验收:** 输出字段分析报告

---

### Task A2: 创建结构化 seed 文件

**Objective:** 创建 `build_seed.json`，参考 JiuwenSwarm 的 `to_seed()` 格式

**Files:**
- Create: `~/.hermes/ecc-loop-seed.json`

**Step 1: 定义 seed 格式**
```json
{
  "version": "1.0",
  "created_at": "ISO timestamp",
  "last_modified": "ISO timestamp",
  "current_phase": "Phase N",
  "execution_state": {
    "active_tasks": [],
    "completed_tasks": [],
    "blocked_tasks": []
  },
  "metrics": {
    "observations_count": 0,
    "skills_generated": 0,
    "patterns_tracked": 0
  }
}
```

**Step 2: 写序列化/反序列化函数**
```python
# 写入 seed
def save_seed(state: dict, path: str):
    state["last_modified"] = datetime.now().isoformat()
    json.dump(state, open(path, "w"), indent=2)

# 读取 seed
def load_seed(path: str) -> dict:
    return json.load(open(path))
```

**验收:** `save_seed()` / `load_seed()` 正常工作，字段完整

---

### Task A3: 修改 STATE.md 更新逻辑使用 seed

**Objective:** 每次更新 STATE.md 时同步更新 seed.json

**Files:**
- Modify: `~/ecc-loop/STATE.md` (末尾添加同步脚本)

**Step 1: 添加同步逻辑**
```bash
# 在每次更新 STATE.md 后执行
python3 -c "
from ecc_seed import save_seed
seed = load_seed('~/.hermes/ecc-loop-seed.json')
seed['current_phase'] = 'Phase X'
seed['execution_state']['completed_tasks'].append('Task X')
save_seed(seed, '~/.hermes/ecc-loop-seed.json')
"
```

**验收:** 更新 STATE.md 后 seed.json 同步更新

---

### Task B1: 分析现有 skill 热加载机制

**Objective:** 理解 Hermes 当前 skill 加载时机

**Files:**
- Read: `hermes-agent/tools/skill_loader.py` 或类似

**Step 1: 查找 skill 加载代码**
```bash
grep -r "load_skill\|reload_skill\|hot_reload" ~/.hermes/hermes-agent/
```

**验收:** 输出 skill 加载时机分析报告

---

### Task B2: 创建 skill 重扫描 cron job

**Objective:** 创建定期重扫描 skill 目录的 cron job

**Files:**
- Create: `~/.hermes/scripts/rescan_skills.sh`

**Step 1: 写重扫描脚本**
```bash
#!/bin/bash
# 检查 skills/ 目录变更
# 如果有新 skill，通知 Hermes 重新加载
# Hermes CLI: hermes skills reload
hermes skills reload 2>/dev/null && echo "Skills reloaded at $(date)"
```

**Step 2: 创建 cron job**
```bash
hermes cron create \
  --name "ECC Skill Rescan" \
  --schedule "0 */1 * * *" \
  --prompt "运行 hermes skills reload" \
  --deliver origin
```

**验收:** cron job 创建成功，每小时自动重扫描

---

### Task B3: 实现 skill 版本追踪

**Objective:** 在 seed 中追踪 skill 版本，支持热回滚

**Files:**
- Modify: `~/.hermes/ecc-loop-seed.json`

**Step 1: 添加 skill 版本字段**
```json
"skills": {
  "instinct-terminal-exec": {
    "version": "1.0.0",
    "created_at": "2026-06-21",
    "last_used": "2026-06-21"
  }
}
```

**验收:** seed 文件包含 skill 版本追踪

---

### Task C1: 分析现有复盘逻辑

**Objective:** 理解当前复盘（reflection）流程

**Files:**
- Read: `ecc_loop/loop_engine/reflection.py`

**Step 1: 读 reflection.py**
- 理解复盘触发时机
- 理解输出格式

**验收:** 输出复盘流程分析

---

### Task C2: 实现分层复盘策略

**Objective:** 实现简单/复杂 query 分流

**Files:**
- Create: `ecc_loop/loop_engine/reflection_tiered.py`

**Step 1: 定义分层策略**
```python
def should_use_fast_path(query: str) -> bool:
    """判断是否走快速路径（≤20 chars，无复杂关键字）"""
    complex_keywords = ["分析", "对比", "设计", "规划", "制定"]
    return len(query) <= 20 and not any(k in query for k in complex_keywords)

def fast_reflection(query: str) -> str:
    """快速路径：直接输出单行结论"""
    return f"基于近期 observations，{query} 的结论是 ..."

def full_reflection(query: str) -> str:
    """完整路径：读取 observations，执行完整分析"""
    ...
```

**Step 2: 集成到复盘入口**
```python
def reflect(query: str) -> str:
    if should_use_fast_path(query):
        return fast_reflection(query)
    return full_reflection(query)
```

**验收:** `pytest tests/test_reflection_tiered.py` 通过

---

## 验证清单

- [ ] Task A1: STATE.md 字段分析报告输出
- [ ] Task A2: seed.json 序列化/反序列化正常
- [ ] Task A3: STATE.md 更新时 seed.json 同步
- [ ] Task B1: skill 加载时机分析完成
- [ ] Task B2: skill 重扫描 cron job 创建成功
- [ ] Task B3: seed.json 包含 skill 版本追踪
- [ ] Task C1: 复盘流程分析完成
- [ ] Task C2: 分层复盘测试通过

---

## 执行顺序

1. **A 系列**（seed 序列化）→ 优先级最高
2. **B 系列**（热更新）→ 独立可执行
3. **C 系列**（分层复盘）→ 依赖 A 系列完成

每 Task 完成后更新 STATE.md。
