# CLI 日志分析工具 — 技术规格说明书

## 1. 项目概述

| 项目 | 内容 |
|------|------|
| **项目名称** | log-analyzer |
| **项目路径** | `/Users/liuzimin/log-analyzer/` |
| **项目类型** | CLI 日志分析工具 |
| **核心功能** | 解析日志文件，提供过滤、搜索、统计和终端可视化功能 |
| **目标用户** | 运维工程师、后端开发者、日志分析人员 |

---

## 2. 技术选型

| 组件 | 推荐方案 | 版本 | 置信度 |
|------|---------|------|:------:|
| 日志框架 | **Loguru** | 0.7.3 | 8/10 |
| CLI 框架 | **Typer** | 0.25.1 | 7/10 |
| 可视化 | **Plotext** | 待安装 | 6/10 |

### 选型理由

1. **Loguru**: CLI 场景零配置优势明显，彩色输出和异常追踪开箱即用
2. **Typer**: Python 3.11 类型提示原生支持，代码简洁且自动生成帮助文档
3. **Plotext**: 终端内直接绘图，无需脱离 CLI 环境

---

## 3. 功能列表

### 3.1 日志解析

- [ ] 支持解析标准格式日志文件（时间戳 + 级别 + 消息）
- [ ] 支持 Loguru 格式日志解析
- [ ] 支持 JSON 格式日志解析（结构化日志）
- [ ] 支持大文件流式读取（> 100MB）
- [ ] 日志级别过滤（DEBUG / INFO / WARNING / ERROR / CRITICAL）

### 3.2 搜索与过滤

- [ ] 关键字全文搜索
- [ ] 正则表达式搜索
- [ ] 按时间范围过滤
- [ ] 按日志级别过滤（可多选）
- [ ] 上下文行查看（-A / -B / -C 参数）

### 3.3 统计分析

- [ ] 日志级别分布统计（计数 + 百分比）
- [ ] 每小时/每天日志量趋势
- [ ] Top N 错误日志统计
- [ ] 关键词出现频率统计

### 3.4 数据可视化（终端 ASCII）

- [ ] 日志级别分布饼图/柱状图
- [ ] 时间线趋势图
- [ ] 终端实时刷新模式（监控模式）
- [ ] 输出导出为 PNG 图片

### 3.5 输出格式

- [ ] 终端彩色输出（默认）
- [ ] JSON 结构化输出（--json）
- [ ] CSV 导出
- [ ] 简洁模式（--quiet，减少冗余信息）

---

## 4. CLI 接口设计

### 4.1 主命令

```bash
log-analyzer [OPTIONS] [LOG_FILE]
```

### 4.2 全局参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--log-level` | TEXT | INFO | 日志级别过滤 |
| `--json` | FLAG | False | JSON 结构化输出 |
| `--quiet` | FLAG | False | 简洁模式 |
| `--output` | PATH | None | 输出文件路径 |

### 4.3 子命令

#### `filter` — 日志过滤

```bash
log-analyzer filter [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--level` | TEXT | None | 按级别过滤（可重复） |
| `--since` | TEXT | None | 起始时间 |
| `--until` | TEXT | None | 结束时间 |
| `--grep` | TEXT | None | 关键字搜索 |
| `--regex` | TEXT | None | 正则表达式 |
| `-A` | INT | 0 | 匹配后行数 |
| `-B` | INT | 0 | 匹配前行数 |
| `-C` | INT | 0 | 上下文行数 |

#### `stats` — 统计分析

```bash
log-analyzer stats [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--by-level` | FLAG | False | 按级别统计 |
| `--by-time` | FLAG | False | 按时间统计 |
| `--top` | INT | 10 | Top N 错误 |
| `--keyword` | TEXT | None | 关键词频率 |

#### `plot` — 可视化

```bash
log-analyzer plot [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--type` | TEXT | bar | 图表类型（bar/pie/line） |
| `--live` | FLAG | False | 实时监控模式 |
| `--export` | PATH | None | 导出 PNG 路径 |
| `--width` | INT | 80 | 图表宽度 |
| `--height` | INT | 20 | 图表高度 |

### 4.4 使用示例

```bash
# 基本查看
log-analyzer app.log

# 过滤 ERROR 日志
log-analyzer filter app.log --level ERROR

# 关键字搜索并显示上下文
log-analyzer filter app.log --grep "timeout" -C 3

# 统计级别分布
log-analyzer stats app.log --by-level

# 绘制时间趋势图
log-analyzer plot app.log --type line

# 实时监控新日志
log-analyzer plot app.log --live

# JSON 输出
log-analyzer filter app.log --level ERROR --json

# 导出统计结果
log-analyzer stats app.log --by-level --output stats.json
```

---

## 5. 输出格式

### 5.1 终端彩色输出

```
[2026-06-24 10:15:32] INFO    | App started on port 8080
[2026-06-24 10:15:33] ERROR   | Connection failed: timeout
[2026-06-24 10:15:33] WARNING | Retrying...
```

### 5.2 JSON 输出

```json
{
  "status": "success",
  "total": 3,
  "level_counts": {
    "INFO": 1,
    "ERROR": 1,
    "WARNING": 1
  },
  "logs": [
    {
      "timestamp": "2026-06-24T10:15:32",
      "level": "INFO",
      "message": "App started on port 8080"
    }
  ]
}
```

### 5.3 CSV 输出

```csv
timestamp,level,message
2026-06-24T10:15:32,INFO,App started on port 8080
2026-06-24T10:15:33,ERROR,Connection failed: timeout
```

---

## 6. 自检清单

### 6.1 功能完整性

- [ ] 日志解析：支持多种格式（标准 / Loguru / JSON）
- [ ] 日志过滤：级别、时间、关键字、正则
- [ ] 统计分析：级别分布、时间趋势、Top N
- [ ] 可视化：终端 ASCII 图表、实时模式、导出 PNG
- [ ] 输出格式：彩色终端 / JSON / CSV

### 6.2 CLI 设计

- [ ] Typer 装饰器风格命令定义
- [ ] 子命令：filter / stats / plot
- [ ] 全局参数：--log-level / --json / --quiet / --output
- [ ] 自动生成帮助文档（--help）
- [ ] 参数类型提示和验证

### 6.3 依赖管理

- [ ] Loguru 0.7.3 已安装验证
- [ ] Typer 0.25.1 已安装验证
- [ ] Plotext 待安装（`uv pip install plotext`）

### 6.4 代码质量

- [ ] Python 3.11 类型提示完整
- [ ] 异常处理完善（日志解析错误提示）
- [ ] 大文件流式处理（内存友好）
- [ ] 路径处理兼容绝对/相对路径

### 6.5 测试验证

- [ ] 构造测试日志文件验证解析
- [ ] 验证过滤条件正确性
- [ ] 验证可视化输出可读性
- [ ] 验证 JSON 输出格式正确

---

## 7. 项目结构

```
/Users/liuzimin/log-analyzer/
├── SPEC.md              # 本规格文档
├── README.md            # 项目文档
├── log_analyzer/        # 主包
│   ├── __init__.py
│   ├── main.py          # 入口，Typer CLI 定义
│   ├── parser.py        # 日志解析器
│   ├── filter.py        # 过滤逻辑
│   ├── stats.py         # 统计分析
│   └── plot.py          # 可视化
├── tests/               # 测试
├── sample_logs/         # 示例日志
├── requirements.txt    # 依赖
└── pyproject.toml       # 项目配置
```

---

## 8. 未来扩展

- [ ] 日志聚合分析（多文件合并）
- [ ] 告警规则配置
- [ ] 输出模板自定义
- [ ] 交互式 TUI 界面
