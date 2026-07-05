# SPEC.md — CLI 文件搜索工具

## 1. 概述与目标

**项目名称**: `fsearch` — Python CLI 文件搜索工具

**核心功能**: 在指定目录中按名称、内容、类型搜索文件，支持正则表达式匹配。

**目标用户**: 开发者日常文件检索、运维脚本集成、自动化工具调用。

---

## 2. 技术选型（Researcher 置信度 >80%，不可更改）

| 组件 | 方案 | 置信度 | 说明 |
|------|------|--------|------|
| 路径遍历 | `pathlib` | 8.3/10 | 面向对象 API，支持 `rglob` 递归 |
| 内容搜索 | `re` (正则) | 8.0/10 | 标准库，预编译匹配 |
| 辅助工具 | `subprocess find` | 8.3/10 | 系统级高速搜索备用 |

**约束**：
- 全部使用 Python 3 标准库，无外部依赖
- 单文件 CLI 入口 (`fsearch.py` 或 `__main__.py`)

---

## 3. 接口规范

### 3.1 CLI 参数

```
fsearch <command> [options] [path]
```

### 3.2 搜索子命令

| 子命令 | 说明 | 关键参数 |
|--------|------|---------|
| `name` | 按文件名搜索 | `-p, --pattern` (正则) |
| `content` | 按文件内容搜索 | `-p, --pattern` (正则) |
| `type` | 按文件类型搜索 | `-e, --ext` (扩展名，如 `py`, `txt`) |

### 3.3 全局选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `path` | 搜索起始目录 | `CWD` (当前目录) |
| `-r, --recursive` | 递归搜索 | `True` |
| `-v, --verbose` | 输出详细日志 | `False` |
| `-h, --help` | 显示帮助 | — |

### 3.4 输出格式

每行一个匹配结果，格式为绝对路径：

```
/absolute/path/to/match/file.py
```

---

## 4. 功能详述

### 4.1 按名称搜索 (`name`)

- 使用 `pathlib.Path.rglob()` 遍历目录树
- 使用 `re.search()` 对文件名做正则匹配
- 支持 glob 通配符简写（`*` 匹配任意字符）

**示例**:
```bash
fsearch name ".*\.py$" /project
fsearch name "test_" /project
```

### 4.2 按内容搜索 (`content`)

- 使用 `pathlib.Path.rglob()` 遍历所有文件
- 使用 `re.search()` 读取文件内容并匹配
- **跳过二进制文件**（根据字节码判断）

**示例**:
```bash
fsearch content "def main" /project
fsearch content "import re" /project
```

### 4.3 按类型搜索 (`type`)

- 使用 `pathlib.Path.rglob()` 配合扩展名过滤
- 支持多扩展名（逗号分隔）

**示例**:
```bash
fsearch type py /project
fsearch type "py,txt,md" /project
```

### 4.4 正则支持

- 所有 `-p, --pattern` 参数均支持正则表达式
- 使用 `re.compile()` 预编译提升性能
- 正则标志：默认 `re.IGNORECASE` 关闭（大小写敏感）

---

## 5. 目录结构

```
file-search/
├── SPEC.md
├── README.md
├── fsearch.py           # CLI 入口，单文件实现
└── tests/
    ├── __init__.py
    ├── test_name_search.py
    ├── test_content_search.py
    └── test_type_search.py
```

---

## 6. 错误处理

| 场景 | 处理方式 |
|------|---------|
| 目录不存在 | 打印错误信息，退出码 1 |
| 无搜索结果 | 静默退出，退出码 0（无输出） |
| 无读取权限 | 跳过该文件，继续搜索 |
| 二进制文件 | 跳过（内容搜索场景） |

---

## 7. 边界情况

1. **空目录**: 无输出，退出码 0
2. **符号链接**: 默认不跟踪（`follow_symlinks=False`）
3. **隐藏文件**: 包含 `.` 开头的文件
4. **大文件**: 内容搜索时，读取前 1MB 进行匹配，超出则截断
5. **空 pattern**: 报错，提示 pattern 不能为空

---

## 8. 验收标准

- [ ] `fsearch name` 正确匹配文件名
- [ ] `fsearch content` 正确搜索文件内容
- [ ] `fsearch type` 正确按扩展名过滤
- [ ] 正则表达式正常工作
- [ ] 递归模式默认开启
- [ ] 错误目录报错退出码 1
- [ ] pytest 测试覆盖 name/content/type 三个场景
- [ ] 无外部依赖，纯标准库实现
- [ ] 单文件 CLI 入口

---

## 9. 自检清单（Writer 交付前检查）

- [x] 技术选型与 Researcher 结论一致（pathlib + re）
- [x] 接口设计完整（name/content/type 三种搜索）
- [x] 文档结构清晰（概述→接口→功能→目录→错误→边界→验收）
- [x] 无遗漏功能项（正则支持、递归、错误处理均已覆盖）
