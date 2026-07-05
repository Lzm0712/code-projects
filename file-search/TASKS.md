# Tasks - CLI 文件搜索工具

## 任务拆分

### ① Session Gate ✅
- 项目目标：CLI 文件搜索工具
- context.md 已加载

### ② 任务拆分

#### Researcher 任务
- 调研 Python 文件搜索方案（os.walk / pathlib / subprocess find）
- 对比搜索性能（ glob / fnmatch / re）
- 置信度打分

#### Writer 任务
- 基于 Researcher 结论写 SPEC.md
- 写 README.md
- **约束：不许改技术选型，变更报 Coordinator**

#### Builder 任务
- 严格按 SPEC.md 实现
- 自检清单
- pytest 测试
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
- agent-log
