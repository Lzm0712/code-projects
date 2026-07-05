# Decisions - CLI 文件搜索工具

## 决策记录

### 技术选型决策
| 决策 | 理由 | 置信度 |
|------|------|--------|
| pathlib 作为路径遍历 | 面向对象 API，8.3/10 | >80%，直接采用 |
| re 作为内容搜索 | 标准库，预编译，8.0/10 | >80%，直接采用 |
| subprocess find 备用 | 性能最强，8.3/10 | >80%，直接采用 |

### 接口设计决策
| 决策 | 理由 |
|------|------|
| 三子命令 name/content/type | 职责分离清晰 |
| pathlib + re 标准库 | 无外部依赖 |
| 单文件 CLI 入口 | 简化部署 |

### 流程执行记录
| 步骤 | 执行结果 |
|------|---------|
| ① Session Gate | ✅ context.md 加载 |
| ② 任务拆分 | ✅ TASKS.md 完成 |
| ③ 角色执行 | ✅ Researcher/Writer/Builder 并行 |
| ④ 置信度审核 | ✅ 全部 >80%，直接采用 |
| ⑤ 自检 & 回查 | ✅ Writer 自检 + 回查 Researcher |
| ⑥ 产出归档 | ✅ outputs/ + pytest 21/21 |
| ⑦ 复盘 | ✅ decisions.md 完成 |

### 流程问题
1. **Builder 在执行时修了 bug**：测试有 2 个 patch 失败后修了，但没报告是什么 bug
2. **接口参数顺序问题**：Builder 报告接口必须是 `fsearch name <path> -p pattern`，与 SPEC 可能不完全一致

### 改进项
1. Builder 自检时发现 bug 应报告给 Coordinator
2. 接口参数顺序以 SPEC.md 为准
