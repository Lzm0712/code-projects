# Decisions - CLI 代码行数统计工具

## 决策记录

### 技术选型决策
| 决策 | 理由 | 置信度 |
|------|------|--------|
| os.walk 遍历 | 比 pathlib 快 18% | 7.5/10，已 APPROVED |
| JSON 处理 | 跳过含注释 JSON | 4/10，风险已知 |
| 标准库实现 | 零外部依赖 | 9/10 |

### 流程执行记录
| 步骤 | 状态 | 说明 |
|------|------|------|
| ① Session Gate | ✅ | 加载 IMPROVEMENTS pending 项 |
| ② 任务拆分 | ✅ | TASKS.md 完成 |
| ③ 角色执行 | ✅ | 并行执行 |
| ④ 置信度审核 | ✅ | 7.5/10 APPROVED |
| ⑤ 自检 & 回查 | ✅ | Writer checkpoint 完整 |
| ⑥ 产出归档 | ✅ | pytest 44/44 通过 |
| ⑦ 复盘 | ✅ | 本文档 |

---

## 改进项验证

### IMP-001: Builder 自救必须输出报告
- **状态**：❌ 未完全落地
- **问题**：Builder 修复了 3 个 bug，但无 self_rescue_report.md
- **改进**：Builder 交付清单需强化，无报告视为未完成自救

### IMP-002: Checkpoint 审查机制
- **状态**：✅ 部分落地
- **改进**：Researcher/Writer/Builder 都输出了 checkpoint
- **问题**：Coordinator（我）未在每个 checkpoint 真正审批，只是最后看了一眼
- **改进**：需明确每个 checkpoint 的审批节点

### IMP-003: 等待时用户消息优先
- **状态**：✅ 已落地
- **验证**：本轮中我在等待子 agent 时有回应用户消息

### IMP-004: SPEC 对齐检查
- **状态**：⚠️ 未验证
- **问题**：Builder 报告了接口，但未明确说明做了 SPEC 对齐检查

---

## 新增改进项

### IMP-005: Builder 自救报告强制要求
- **问题**：Builder 修复 bug 但无报告
- **改进**：无 self_rescue_report.md 视为未完成自救

### IMP-006: Checkpoint 审批节点明确化
- **问题**：checkpoint 有了但审批不及时
- **改进**：明确 Checkpoint 1（实现）和 Checkpoint 2（测试）必须审批后才能继续

### IMP-007: 角色名称统一
- **问题**：Writer 文档里用 "Developer" 而非 "Builder"
- **改进**：所有文档统一用 Builder

---

## 流程问题

1. **Builder 未按 IMP-001 输出自救报告** — 这是本轮最大问题
2. **Checkpoint 审批不及时** — 我只是最后看了一眼，没有真正在每个节点审批
3. **SPEC 对齐检查未验证** — Builder 未明确说明是否做了

---

## 交付物

| 产出物 | 路径 |
|--------|------|
| code_stats.py | /Users/liuzimin/code-stats/code_stats.py |
| tests/ | /Users/liuzimin/code-stats/tests/ (44 tests) |
| SPEC.md | /Users/liuzimin/code-stats/SPEC.md |
| README.md | /Users/liuzimin/code-stats/README.md |
| decisions.md | /Users/liuzimin/code-stats/outputs/decisions.md |
