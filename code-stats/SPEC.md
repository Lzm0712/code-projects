# 代码行数统计工具 SPEC

## 1. 项目概述

**项目名称**: code-stats  
**类型**: CLI 命令行工具  
**核心功能**: 统计指定目录中代码文件的行数，按编程语言分类，支持跳过空行和注释行  
**目标用户**: 开发者、项目经理、技术负责人

---

## 2. 技术选型

### 2.1 遍历方案

| 方案 | 选择 | 理由 |
|------|------|------|
| os.walk | ✅ 采用 | 速度快（比 pathlib 快 ~18%），内存占用低，目录过滤控制灵活 |
| pathlib | ❌ 不采用 | 速度稍慢，API 虽简洁但本项目性能优先 |

### 2.2 依赖策略

| 策略 | 选择 | 理由 |
|------|------|------|
| 标准库 | ✅ 仅用标准库 | 零外部依赖，轻量级，易部署 |
| 外部库 | ❌ 不引入 | 避免依赖管理复杂度 |

---

## 3. 支持语言

| 语言 | 扩展名 | 单行注释 | 多行注释 | 备注 |
|------|--------|----------|----------|------|
| Python | .py | `#` | `"""..."""` `'''...'''` | docstring 需状态机追踪 |
| JavaScript | .js | `//` | `/* ... */` | 块注释需跨行状态 |
| TypeScript | .ts | `//` | `/* ... */` | 同 JavaScript |
| Go | .go | `//` | `/* ... */` | 注释语法简单规范 |
| Rust | .rs | `//` | `/* ... */` | 文档注释 `///` `//!` |
| JSON | .json | 无 | 无 | JSON 标准不支持注释，跳过含注释的 JSON 文件 |
| YAML | .yaml / .yml | `#` | 无 | 行注释语义清晰 |
| Markdown | .md | `#` | `<!-- ... -->` | `#` 歧义（标题/注释） |

---

## 4. 功能规格

### 4.1 核心功能

1. **目录遍历**
   - 使用 `os.walk()` 递归遍历指定目录
   - 跳过隐藏目录（以 `.` 开头，如 `.git/`、`node_modules/`）
   - 跳过常见非源码目录（`__pycache__/`、`venv/`、`env/`）

2. **文件过滤**
   - 按扩展名匹配支持的语言
   - 忽略二进制文件（通过扩展名白名单）

3. **行数统计**
   - 统计规则：仅计入**有效代码行**
   - 跳过：空行（纯空白或仅含缩进的行）
   - 跳过：注释行（单行注释、多行注释的一部分）

4. **分类汇总**
   - 按语言分组输出行数统计
   - 输出总行数

### 4.2 CLI 接口

```bash
python code_stats.py <目录路径> [--verbose]
```

| 参数 | 说明 |
|------|------|
| `<目录路径>` | 必选，要统计的代码目录 |
| `--verbose` | 可选，显示详细输出（每个文件的行数） |
| `--help` | 显示帮助信息 |

### 4.3 输出格式

```
Language      Files    Lines
--------------------------------
Python          12      1523
JavaScript       8       456
Go               3       210
Markdown        15       890
--------------------------------
Total           38      3079
```

---

## 5. 注释识别算法

### 5.1 单行注释识别

```python
# Python / YAML / Markdown: # 注释
re.compile(r'^\s*#')

# JavaScript / Go / Rust: // 注释
re.compile(r'^\s*//')
```

### 5.2 多行注释状态机

```python
class LineClassifier:
    def __init__(self, language):
        self.in_block_comment = False
        self.block_end_pattern = None  # */ """ 或 '''

    def classify(self, line):
        if self.in_block_comment:
            if self._block_ends(line):
                self.in_block_comment = False
            return 'comment'
        if self._block_starts(line):
            self.in_block_comment = True
            return 'comment'
        return 'code'
```

### 5.3 空行判断

```python
def is_blank_line(line: str) -> bool:
    return line.strip() == ''
```

---

## 6. 性能设计

| 优化点 | 策略 |
|--------|------|
| 文件读取 | 小文件用 `f.readlines()`，大文件（>10MB）用逐行迭代 |
| 目录遍历 | os.walk 增量迭代，内存占用低 |
| 目录过滤 | 提前排除 `.git/` `node_modules/` 等无效目录 |
| 并行化 | 可选：使用 `concurrent.futures.ProcessPoolExecutor` 按文件级并行 |

---

## 7. 置信度评估

| 模块 | 置信度 | 风险点 |
|------|--------|--------|
| os.walk 遍历 | 9/10 | 需手动过滤文件类型 |
| 空行判断 | 10/10 | 无歧义 |
| Python 注释识别 | 8/10 | docstring 嵌套 |
| JS/Go/Rust 注释 | 7/10 | 块注释跨行状态 |
| YAML 注释识别 | 8/10 | 简单明确 |
| JSON 处理 | 4/10 | 跳过含注释的 JSON 文件 |
| Markdown 处理 | 6/10 | `#` 语义歧义 |

**综合置信度: 7.5/10**

---

## 8. 目录结构

```
/Users/liuzimin/code-stats/
├── SPEC.md                  # 本规格文档
├── README.md                # 用户文档
├── code_stats.py            # 主程序入口
├── src/
│   ├── __init__.py
│   ├── walker.py            # os.walk 遍历模块
│   ├── counter.py           # 行数统计模块
│   ├── classifier.py        # 注释/空行分类器
│   └── languages.py         # 语言定义与扩展名映射
└── tests/
    ├── __init__.py
    ├── test_classifier.py
    ├── test_counter.py
    └── test_walker.py
```

---

## 9. 验收标准

1. ✅ CLI 工具可从命令行运行
2. ✅ 统计指定目录的代码行数
3. ✅ 按语言分类输出
4. ✅ 跳过空行
5. ✅ 跳过单行注释（`#`、`//`）
6. ✅ 跳过多行注释块（`"""`、`'''`、`/* */`、`<!-- -->`）
7. ✅ 使用 os.walk 遍历
8. ✅ 仅使用标准库（无外部依赖）
9. ✅ 输出格式清晰可读
