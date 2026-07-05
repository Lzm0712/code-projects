# fsearch — CLI 文件搜索工具

Python 标准库实现的 CLI 文件搜索工具，支持按**名称**、**内容**、**类型**搜索文件，支持正则表达式。

---

## 特性

- 🚀 **纯标准库** — 无外部依赖，Python 3 内置
- 🔍 **三种搜索模式** — 名称 / 内容 / 类型
- ⭐ **正则支持** — 所有 pattern 参数支持正则表达式
- 📁 **递归搜索** — 默认递归遍历子目录
- ⚡ **高性能** — 基于 `pathlib` + `re` 标准库

---

## 安装

无需安装，直接运行：

```bash
# 方式一：直接运行
python fsearch.py name "*.py" /path/to/search

# 方式二：添加执行权限（Linux/macOS）
chmod +x fsearch.py
./fsearch.py name "*.py" /path/to/search
```

---

## 使用方法

```
fsearch <command> [options] [path]
```

### 子命令

| 子命令 | 说明 |
|--------|------|
| `name` | 按文件名搜索 |
| `content` | 按文件内容搜索 |
| `type` | 按文件类型（扩展名）搜索 |

### 全局选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `path` | 搜索起始目录 | 当前目录 |
| `-r, --recursive` | 递归搜索 | True |
| `-v, --verbose` | 输出详细日志 | False |
| `-h, --help` | 显示帮助 | — |

---

## 示例

### 按名称搜索

```bash
# 搜索所有 .py 文件
fsearch name ".*\.py$"

# 搜索以 test 开头的文件
fsearch name "test_.*" /project

# 正则匹配（忽略大小写）
fsearch name "README" /project
```

### 按内容搜索

```bash
# 搜索包含 "def main" 的文件
fsearch content "def main" /project

# 搜索包含 "import re" 的文件
fsearch content "import re" /project

# 搜索特定模式
fsearch content "class.*Error" /project
```

### 按类型搜索

```bash
# 搜索所有 .py 文件
fsearch type py /project

# 搜索多种类型（逗号分隔）
fsearch type "py,txt,md" /project

# 搜索所有 .json 文件
fsearch type json /project
```

### 其他选项

```bash
# 非递归搜索（仅当前目录）
fsearch name "*.py" /project -r False

# 显示详细日志
fsearch content "pattern" /project -v

# 指定搜索路径
fsearch type py /home/user/myproject
```

---

## 输出格式

每行一个匹配结果的绝对路径：

```
/absolute/path/to/match/file1.py
/absolute/path/to/match/file2.py
/absolute/path/to/match/file3.py
```

无匹配结果时无输出（静默退出，退出码 0）。

---

## 错误处理

| 场景 | 行为 |
|------|------|
| 目录不存在 | 打印错误信息，退出码 1 |
| 无搜索结果 | 静默退出，退出码 0 |
| 无读取权限 | 自动跳过该文件 |
| 二进制文件 | 自动跳过（内容搜索时） |

---

## 技术细节

### 使用的标准库

| 模块 | 用途 |
|------|------|
| `pathlib` | 目录遍历、路径操作 |
| `re` | 正则表达式匹配 |
| `argparse` | CLI 参数解析 |
| `sys` | 系统退出码 |

### 搜索策略

- **名称搜索**: `pathlib.Path.rglob()` + `re.search()` 对路径字符串匹配
- **内容搜索**: `pathlib.Path.rglob()` 遍历所有文件，`re.search()` 读取内容匹配
- **类型搜索**: `pathlib.Path.rglob()` + 扩展名过滤

### 性能说明

- 使用 `pathlib.rglob()` 底层基于 `os.scandir`，高效遍历
- 正则表达式使用 `re.compile()` 预编译
- 内容搜索对大文件（>1MB）进行截断读取

---

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行指定测试
pytest tests/test_name_search.py -v

# 查看测试覆盖率
pytest tests/ --cov=fsearch --cov-report=term-missing
```

### 测试用例覆盖

| 测试文件 | 覆盖场景 |
|---------|---------|
| `test_name_search.py` | 文件名正则匹配、glob 模式 |
| `test_content_search.py` | 文件内容搜索、二进制跳过 |
| `test_type_search.py` | 扩展名过滤、多类型支持 |

---

## 目录结构

```
file-search/
├── SPEC.md              # 详细技术规格
├── README.md            # 本文档
├── fsearch.py           # CLI 入口
└── tests/
    ├── __init__.py
    ├── test_name_search.py
    ├── test_content_search.py
    └── test_type_search.py
```

---

## 许可证

MIT License
