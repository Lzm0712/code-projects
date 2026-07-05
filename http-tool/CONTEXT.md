# Context - HTTP 请求工具

## 项目目标
实现一个 CLI HTTP 请求工具，类似 curl，支持 GET/POST/PUT/DELETE。

## 约束
- Python 实现
- 标准库为主（urllib）
- 支持 headers 和 body
- JSON 响应格式化
- pytest 测试

## 质量标准（上一轮改进项验证）
- **IMP-001**: Builder 自救必须输出 self_rescue_report.md（验证：如需自救是否输出）
- **IMP-002**: Checkpoint 审查机制（验证：Checkpoint 1/2 是否审批）
- **IMP-004**: SPEC 对齐检查（验证：Builder 是否做对齐）

## 流程
Session Gate → 任务拆分 → 角色执行 → 置信度审核 → 自检&回查 → 产出归档 → 复盘 → 持续改进循环
