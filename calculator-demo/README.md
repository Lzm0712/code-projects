# Python Calculator

一个简洁的 Python 四则运算计算器，支持括号优先级和命令行使用。

A simple Python calculator supporting basic arithmetic operations (+, -, *, /) with parentheses for precedence and command-line interface.

---

## 特性 | Features

- ➕ 加法、➖ 减法、✖️ 乘法、➗ 除法
- 📐 括号优先级处理
- 🔢 支持浮点数运算
- ⌨️ 命令行交互
- 📦 可作为库导入使用

---

## 快速开始 | Quick Start

### 安装 | Installation

无需安装，直接下载 `calculator.py` 即可使用：

No installation required, just download `calculator.py`:

```bash
# 克隆项目
git clone https://github.com/example/calculator-demo.git
cd calculator-demo
```

### 使用方法 | Usage

#### 命令行模式 | CLI Mode

```bash
python calculator.py "2 + 3 * 4"
# 输出: 2 + 3 * 4 = 14

python calculator.py "(2 + 3) * 4"
# 输出: (2 + 3) * 4 = 20
```

#### 作为库使用 | As a Library

```python
from calculator import calculate

result = calculate("2 + 3 * 4")
print(result)  # 14
```

---

## API 参考 | API Reference

### `calculate(expression: str) -> Union[float, int]`

主要计算函数，解析并求值表达式字符串。

Main calculation function that parses and evaluates an expression string.

**参数 | Parameters:**
- `expression` (str): 数学表达式，如 `"2 + 3 * 4"`

**返回值 | Returns:**
- `int`: 结果为整数时返回 int 类型
- `float`: 结果为小数时返回 float 类型

**异常 | Raises:**
- `CalculatorError`: 表达式无效时抛出

```python
calculate("2 + 3")       # => 5
calculate("10 / 3")      # => 3.333...
calculate("(2 + 3) * 4") # => 20
```

### `CalculatorError`

自定义异常类，用于处理计算器相关错误。

Custom exception class for calculator-related errors.

```python
from calculator import calculate, CalculatorError

try:
    result = calculate("1 / 0")
except CalculatorError as e:
    print(e)  # Division by zero
```

---

## 示例 | Examples

### 1. 基本加法 | Basic Addition

```python
calculate("2 + 3")        # => 5
calculate("10 + 20 + 30") # => 60
```

### 2. 运算符优先级 | Operator Precedence

```python
# 乘法优先于加法
# Multiplication has higher precedence than addition
calculate("2 + 3 * 4")    # => 14  (2 + 12)
calculate("10 - 6 / 2")  # => 7   (10 - 3)
```

### 3. 括号控制优先级 | Parentheses Control Precedence

```python
# 括号内的运算优先
calculate("(2 + 3) * 4")      # => 20
calculate("2 * (3 + 4) - 6 / 2")  # => 11
calculate("((2 + 3))")        # => 5
```

### 4. 浮点数运算 | Floating Point Operations

```python
calculate("7 / 2")       # => 3.5
calculate("2.5 + 3.5")   # => 6.0
calculate("3.14 * 2")    # => 6.28
```

### 5. 负数处理 | Negative Numbers

```python
calculate("3 - 8")       # => -5
calculate("-5 + 3")      # => -2
calculate("-2 * -3")      # => 6
```

### 6. 更多示例 | More Examples

```python
calculate("24 / 3 / 2")      # => 4
calculate("12 / 3 * 2")      # => 8
calculate("(2 + 3) * (4 + 1)")  # => 25
calculate("-2 * -3 + 1")     # => 7
```

---

## 运行测试 | Run Tests

```bash
# 安装 pytest（如未安装）
pip install pytest

# 运行所有测试
pytest test_calculator.py -v
```

---

## 项目结构 | Project Structure

```
calculator-demo/
├── calculator.py      # 主程序文件 | Main program file
├── test_calculator.py # 单元测试 | Unit tests
├── README.md          # 项目文档 | Project documentation
└── .pytest_cache/     # 测试缓存 | Test cache
```

---

## 贡献指南 | Contributing

欢迎提交 Issue 和 Pull Request！

Contributions are welcome! Feel free to submit Issues and Pull Requests.

### 开发流程 | Development Workflow

1. **Fork** 本仓库
2. **创建特性分支**: `git checkout -b feature/your-feature`
3. **提交更改**: `git commit -m 'Add some feature'`
4. **推送分支**: `git push origin feature/your-feature`
5. **创建 Pull Request**

### 提交规范 | Commit Convention

- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 代码重构

### 报告问题 | Reporting Issues

请包含以下信息：
- Python 版本
- 操作系统
- 复现步骤
- 期望结果与实际结果

Please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual results

---

## 许可证 | License

MIT License

---

## 版本 | Version

v1.0.0
