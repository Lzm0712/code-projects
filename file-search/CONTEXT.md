# Context - CLI 文件搜索工具

## 项目目标
实现一个 CLI 文件搜索工具，支持按名称、内容、类型搜索。

## 约束
- Python 实现
- 单文件 CLI 入口
- 无外部依赖（标准库优先）
- 支持正则搜索
- 测试覆盖

## 质量标准
- 置信度 gate：>80% 直接采用，<40% 人工判断
- Writer 自检四重检查
- 产出归档到 outputs/
- 复盘记录 decisions.md

## 角色
- Coordinator：任务拆分、审查、汇总
- Researcher：调研搜索方案
- Writer：写 SPEC/文档
- Builder：实现功能

## 流程
Session Gate → 任务拆分 → 角色执行 → 置信度审核 → 自检&回查 → 产出归档 → 复盘
