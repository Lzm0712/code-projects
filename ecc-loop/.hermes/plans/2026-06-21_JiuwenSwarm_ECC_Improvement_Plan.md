# JiuwenSwarm → ECC Loop 改进实施计划

**Goal:** 基于 JiuwenSwarm 研究结果，对 ECC Loop 实施三项关键改进
**执行模式:** Loop Engineering — STATE.md 驱动，cron job 自动化

---

## 实际环境

- ECC Loop skill: `~/.hermes/skills/ecc-to-hermes-loop/`
- observations: `~/.hermes/observations.jsonl` (18条)
- Hermes agent: `~/.hermes/hermes-agent/`
- Skills dir: `~/.hermes/skills/`

---

## 改进架构（参考 JiuwenSwarm）

```
JiuwenSwarm Pattern → ECC Loop 适配

1. JiuwenSwarm Provider Registry → ECC observations tracker
2. JiuwenSwarm Evolution Trigger → ECC evolution_candidates.jsonl
3. JiuwenSwarm Skill Hub → ECC ~/.hermes/skills/

Pipeline:
observations.jsonl
    → evolution_trigger.py (counter/ratio/external)
    → evolution_candidates.jsonl
    → skill_generator.py
    → ~/.hermes/skills/new-skill/
    → cron job 定期运行
```

---

## Phase 1: 理解现有 observations 结构

### Task 1: 读 observations.jsonl 格式

**Objective:** 理解当前 observation 记录结构

**Files:**
- Read: `~/.hermes/observations.jsonl`

**Step 1: 读取所有 observation**
```bash
wc -l ~/.hermes/observations.jsonl
cat ~/.hermes/observations.jsonl | python3 -c "import sys,json; [print(json.loads(l))] for l in sys.stdin"
```

**Step 2: 分析字段**
- 时间戳
- 工具名
- 参数签名
- 结果摘要
- 触发计数

**验收:** 输出 observation 字段分析报告

---

## Phase 2: evolution_trigger 脚本

### Task 2: 创建 evolution_trigger.py

**Objective:** 实现固化触发器，参考 JiuwenSwarm 的 trigger 机制

**Files:**
- Create: `~/.hermes/scripts/evolution_trigger.py`

**Step 1: 定义数据结构**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

@dataclass
class EvolutionCandidate:
    observation_ids: list[str]
    summary: str
    trigger: Literal["counter", "ratio", "external", "search_hit"]
    confidence: float
    pattern_key: str
    created_at: datetime = field(default_factory=datetime.now)
```

**Step 2: 实现 CounterTrigger**
```python
class CounterTrigger:
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self._state_file = Path.home() / ".hermes" / "evolution_counter.json"
    
    def record(self, pattern_key: str) -> bool:
        # 读计数器
        # +1
        # 写回
        # 返回是否达到 threshold
```

**Step 3: 实现 scan_observations**
```python
def scan_observations(obs_path: str) -> list[EvolutionCandidate]:
    # 读取 observations.jsonl
    # 提取 pattern_key (工具名 + 主要参数 hash)
    # 对每个 pattern 调用 counter_trigger.record()
    # 返回达到阈值的 candidates
```

**验收:** 脚本可独立运行，输出 candidates 到 `evolution_candidates.jsonl`

---

### Task 3: 集成到 cron job

**Objective:** 创建定期运行的 evolution cron job

**Files:**
- Create cron job via `hermes cron create`

**Step 1: 创建触发器脚本**
- 脚本路径: `~/.hermes/scripts/run_evolution_trigger.sh`
- 功能: 运行 evolution_trigger.py

**Step 2: 创建 cron job**
```bash
hermes cron create \
  --name "ECC Evolution Trigger" \
  --schedule "0 */2 * * *" \
  --prompt "运行 ~/.hermes/scripts/run_evolution_trigger.sh" \
  --deliver origin
```

**验收:** cron job 创建成功，每2小时自动扫描 observations

---

## Phase 3: skill_generator 脚本

### Task 4: 创建 skill_generator.py

**Objective:** 将 EvolutionCandidate 转换为可执行的 skill 文件

**Files:**
- Create: `~/.hermes/scripts/skill_generator.py`

**Step 1: 读取 candidates**
```python
def load_candidates(path: str) -> list[EvolutionCandidate]:
    with open(path) as f:
        return [EvolutionCandidate(**json.loads(l)) for l in f]
```

**Step 2: 生成 skill 目录**
```python
def generate_skill(candidate: EvolutionCandidate) -> Path:
    skill_name = f"instinct-{candidate.pattern_key[:16]}"
    skill_dir = Path.home() / ".hermes" / "skills" / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # 写 SKILL.md
    (skill_dir / "SKILL.md").write_text(SKILL_TEMPLATE.format(...))
    return skill_dir
```

**Step 3: SKILL.md 模板**
```markdown
---
name: {skill_name}
description: "{summary}"
trigger: evolution-{trigger}
version: 1.0.0
---

# {skill_name}

## 来源
- 触发类型: {trigger}
- 置信度: {confidence}
- Pattern: `{pattern_key}`

## 经验摘要
{summary}

## 验证
{verification_steps}
```

**验收:** `skill_generator.py` 可将 candidate 转换为 `~/.hermes/skills/instinct-xxx/SKILL.md`

---

### Task 5: 创建完整 pipeline 脚本

**Objective:** 将 trigger + generation 串联成完整 pipeline

**Files:**
- Create: `~/.hermes/scripts/run_evolution_pipeline.sh`

**Step 1: Pipeline 流程**
```bash
#!/bin/bash
# 1. 扫描 observations，生成 candidates
python3 ~/.hermes/scripts/evolution_trigger.py

# 2. 读取 candidates，生成 skills
python3 ~/.hermes/scripts/skill_generator.py

# 3. 报告结果
echo "Evolution pipeline complete"
```

**Step 2: 更新 cron job**
- 将 cron job 的脚本从单独 trigger 改为 pipeline 脚本

**验收:** pipeline 可完整运行，生成 skill 文件

---

## Phase 4: 验证与文档

### Task 6: 运行完整验证

**Objective:** 执行 pipeline，验证 skill 生成

**Step 1: 手动运行 pipeline**
```bash
bash ~/.hermes/scripts/run_evolution_pipeline.sh
```

**Step 2: 检查输出**
- `evolution_candidates.jsonl` 是否有新记录
- `~/.hermes/skills/instinct-*/` 是否有新 skill

**Step 3: 验证 skill 格式**
- skill 可被 `hermes skills list` 识别

**验收:** pipeline 成功执行，生成有效 skill

---

## 验证清单

- [ ] Task 1: observation 字段分析报告输出
- [ ] Task 2: evolution_trigger.py 独立运行成功
- [ ] Task 3: cron job 创建成功
- [ ] Task 4: skill_generator.py 生成有效 SKILL.md
- [ ] Task 5: pipeline 脚本串联成功
- [ ] Task 6: 完整 pipeline 执行验证通过
