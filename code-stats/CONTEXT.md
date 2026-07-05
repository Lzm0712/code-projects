# Context - CLI 代码行数统计工具

## 项目目标
实现一个 CLI 代码行数统计工具，统计目录中各语言的代码行数。

## 约束
- Python 实现
- 标准库为主
- 支持语言：Python, JavaScript, TypeScript, Go, Rust, JSON, YAML, Markdown
- 跳过空行和注释
- pytest 测试

## 质量标准（上一轮改进项验证）
- **IMP-001**: Builder 自救必须输出 self_rescue_report.md（验证：本轮如需自救是否输出）
- **IMP-002**: Checkpoint 审查机制（验证：本轮是否执行）
- **IMP-003**: 等待时用户消息优先（验证：等待时是否响应）
- **IMP-004**: SPEC 对齐检查（验证：Builder 是否做对齐）

## 流程
Session Gate → 任务拆分 → 角色执行 → 置信度审核 → 自检&回查 → 产出归档 → 复盘 → 持续改进循环
