# Log Analyzer

命令行日志分析工具 — 解析、过滤、统计、可视化，一站式完成。

## 功能特性

- 🔍 **日志解析**: 支持标准格式、Loguru、JSON 格式日志
- 🎯 **灵活过滤**: 级别、时间范围、关键字、正则表达式
- 📊 **统计分析**: 级别分布、时间趋势、Top N 错误
- 📈 **终端可视化**: ASCII 图表、实时监控、PNG 导出

## 技术栈

| 组件 | 方案 | 版本 |
|------|------|------|
| 日志框架 | Loguru | 0.7.3 |
| CLI 框架 | Typer | 0.25.1 |
| 可视化 | Plotext | 待安装 |

## 安装

```bash
# 克隆项目
git clone https://github.com/example/log-analyzer.git
cd log-analyzer

# 安装依赖
uv pip install loguru typer plotext rich

# 或使用 pip
pip install loguru typer plotext rich
```

## 快速开始

### 基本查看

```bash
log-analyzer app.log
```

### 日志过滤

```bash
# 过滤 ERROR 级别
log-analyzer filter app.log --level ERROR

# 关键字搜索 + 上下文
log-analyzer filter app.log --grep "timeout" -C 3

# 正则表达式
log-analyzer filter app.log --regex "error-\d+"
```

### 统计分析

```bash
# 级别分布统计
log-analyzer stats app.log --by-level

# 时间趋势
log-analyzer stats app.log --by-time

# Top 10 错误
log-analyzer stats app.log --top 10
```

### 可视化

```bash
# 级别分布柱状图
log-analyzer plot app.log --type bar

# 时间线趋势
log-analyzer plot app.log --type line

# 实时监控
log-analyzer plot app.log --live

# 导出 PNG
log-analyzer plot app.log --export chart.png
```

### 输出格式

```bash
# JSON 输出
log-analyzer filter app.log --level ERROR --json

# 简洁模式
log-analyzer filter app.log --quiet

# 导出到文件
log-analyzer stats app.log --by-level --output stats.json
```

## CLI 命令

### 全局参数

| 参数 | 说明 |
|------|------|
| `--log-level` | 日志级别过滤 |
| `--json` | JSON 结构化输出 |
| `--quiet` | 简洁模式 |
| `--output` | 输出文件路径 |

### 子命令

#### `filter` — 日志过滤

```
--level TEXT      按级别过滤（可重复）
--since TEXT      起始时间
--until TEXT      结束时间
--grep TEXT       关键字搜索
--regex TEXT      正则表达式
-A INT            匹配后行数
-B INT            匹配前行数
-C INT            上下文行数
```

#### `stats` — 统计分析

```
--by-level        按级别统计
--by-time         按时间统计
--top INT         Top N 错误（默认 10）
--keyword TEXT    关键词频率
```

#### `plot` — 可视化

```
--type TEXT       图表类型：bar / pie / line（默认 bar）
--live            实时监控模式
--export PATH     导出 PNG 路径
--width INT       图表宽度（默认 80）
--height INT      图表高度（默认 20）
```

## 示例日志格式

```
[2026-06-24 10:15:32] INFO    | App started on port 8080
[2026-06-24 10:15:33] ERROR   | Connection failed: timeout
[2026-06-24 10:15:34] WARNING | Retrying...
```

## 项目结构

```
log-analyzer/
├── log_analyzer/      # 主包
│   ├── main.py        # CLI 入口
│   ├── parser.py      # 日志解析
│   ├── filter.py      # 过滤逻辑
│   ├── stats.py       # 统计
│   └── plot.py        # 可视化
├── tests/             # 测试
├── sample_logs/       # 示例日志
└── requirements.txt   # 依赖
```

## 依赖

```
loguru>=0.7.0
typer>=0.25.0
plotext>=0.0.1
rich>=13.0.0
```

## License

MIT
