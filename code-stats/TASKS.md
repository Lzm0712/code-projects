# Tasks - CLI 代码行数统计工具

## 任务拆分

### ① Session Gate ✅
- 项目目标：CLI 代码行数统计工具
- context.md 已加载
- 上一轮改进项已加载（IMP-001~004）

### ② 任务拆分

#### Researcher 任务
- 调研代码行数统计方案（os.walk / pathlib / tokenize / tree-sitter）
- 对比各语言注释识别方式
- 置信度打分

#### Writer 任务
- 基于 Researcher 结论写 SPEC.md
- 写 README.md
- **约束：不许改技术选型，变更报 Coordinator**

#### Builder 任务
- 严格按 SPEC.md 实现
- **Checkpoint 1**：实现完成，输出 checkpoint 报告
- **Checkpoint 2**：测试完成，输出 checkpoint 报告
- **如需自救**：必须输出 self_rescue_report.md
- **交付前**：SPEC 对齐检查
- **约束：不许改 SPEC**

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
- 更新 dashboard

### ⑦ 复盘
- decisions.md
- 验证 IMP-001~004 是否落地

### 持续改进
- 改进项更新到 IMPROVEMENTS.md
