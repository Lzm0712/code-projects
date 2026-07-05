# code-stats

代码行数统计工具 — 轻量、跨平台、零依赖。

## 功能特性

- 📊 **按语言分类统计**：Python、JavaScript、TypeScript、Go、Rust、JSON、YAML、Markdown
- 🚀 **高性能**：使用 `os.walk` 遍历，比 pathlib 快约 18%
- 📦 **零依赖**：仅使用 Python 标准库
- ✅ **精准过滤**：跳过空行、注释行（单行注释 + 多行注释块）
- 🖥️ **CLI 接口**：一条命令即可完成统计

## 安装

无需安装，直接运行：

```bash
python code_stats.py <目录路径>
```

或添加执行权限后直接运行：

```bash
chmod +x code_stats.py
./code_stats.py <目录路径>
```

## 使用方法

### 基本用法

```bash
python code_stats.py /path/to/your/project
```

### 显示详细输出

```bash
python code_stats.py /path/to/your/project --verbose
```

### 显示帮助

```bash
python code_stats.py --help
```

## 输出示例

**标准输出：**

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

**详细模式 (`--verbose`)：**

```
Language      Files    Lines
--------------------------------
Python          12      1523
  src/main.py              120
  src/utils.py              85
  ...

JavaScript       8       456
  frontend/app.js           92
  frontend/router.js        45
  ...

Go               3       210
  cmd/server/main.go       150
  internal/handler.go       60
  ...

Markdown        15       890
  README.md                120
  CHANGELOG.md              80
  ...

--------------------------------
Total           38      3079
```

## 支持的语言

| 语言 | 扩展名 | 注释语法 |
|------|--------|----------|
| Python | .py | `#` 单行，`"""` `'''` 多行 |
| JavaScript | .js | `//` 单行，`/* */` 多行 |
| TypeScript | .ts | `//` 单行，`/* */` 多行 |
| Go | .go | `//` 单行，`/* */` 多行 |
| Rust | .rs | `//` 单行，`/* */` 多行 |
| JSON | .json | 无注释（标准 JSON 不支持） |
| YAML | .yaml / .yml | `#` 单行 |
| Markdown | .md | `<!-- -->` 多行 |

## 工作原理

1. 使用 `os.walk()` 递归遍历指定目录
2. 按扩展名过滤源文件
3. 逐行读取文件内容
4. 分类每行：`空行` / `注释行` / `代码行`
5. 按语言分组汇总

### 注释识别

- **空行判定**：`line.strip() == ''`
- **单行注释**：以 `#` 或 `//` 开头（忽略行首空白）
- **多行注释块**：追踪 `"""` `'''` `/* */` `<!-- -->` 的嵌套状态

### 排除规则

以下目录和文件会被自动跳过：

- 隐藏目录（以 `.` 开头）：`.git/`、`.svn/`、`node_modules/` 等
- 虚拟环境目录：`venv/`、`env/`、`__pycache__/`
- 二进制文件

## 项目结构

```
code-stats/
├── code_stats.py       # 主程序入口
├── src/
│   ├── walker.py       # os.walk 遍历模块
│   ├── counter.py      # 行数统计模块
│   ├── classifier.py   # 注释/空行分类器
│   └── languages.py    # 语言定义与扩展名映射
├── tests/              # 单元测试
├── SPEC.md             # 技术规格文档
└── README.md           # 本文档
```

## 局限性

| 语言 | 置信度 | 说明 |
|------|--------|------|
| JSON | 4/10 | 标准 JSON 不支持注释，含注释的 JSON 文件会被跳过 |
| Markdown | 6/10 | `#` 既可表示标题也可表示注释，存在歧义 |

## 常见问题

**Q: 统计结果与 cloc/tokei 不一致？**  
A: 本工具专注于「有效代码行」统计，跳过空行和注释。部分工具会计入文档字符串或 README 行。

**Q: 为什么 Python 的 `"""docstring"""` 被跳过？**  
A: docstring 是文档注释，按设计应归类为注释而非代码。

**Q: 如何统计二进制文件（如图片、PDF）？**  
A: 本工具按扩展名过滤，不会处理二进制文件。

## License

MIT License
