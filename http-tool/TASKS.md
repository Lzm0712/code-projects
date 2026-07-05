# Tasks - HTTP 请求工具

## 任务拆分

### ① Session Gate ✅
- 项目目标：CLI HTTP 请求工具
- context.md 已加载
- 上一轮改进项已加载（IMP-001/002/004 需验证）

### ② 任务拆分

#### Researcher 任务
- 调研 Python HTTP 方案（urllib / requests / httpx）
- 对比同步/异步
- 置信度打分

#### Writer 任务
- 基于 Researcher 结论写 SPEC.md + README.md
- **约束：不许改技术选型，变更报 Coordinator**

#### Builder 任务
- 严格按 SPEC.md 实现
- **Checkpoint 1（实现）**：输出 checkpoint 报告，**Coordinator APPROVED 后继续**
- **Checkpoint 2（测试）**：输出 checkpoint 报告，**Coordinator APPROVED 后交付**
- **如需自救**：必须输出 self_rescue_report.md
- **交付前**：SPEC 对齐检查

### ③ 角色执行
Researcher / Writer / Builder 并行

### ④ 置信度审核
- Coordinator 审查 Researcher 置信度
- >80% 直接采用，<40% 人工判断

### ⑤ 自检 & 回查
- Writer 四重检查
- 回查 Researcher 结论

### ⑥ 产出归档
- 归档到 outputs/
- pytest 验证

### ⑦ 复盘
- decisions.md
- 验证 IMP-001/002/004 是否落地

### 持续改进
- 改进项更新到 IMPROVEMENTS.md
