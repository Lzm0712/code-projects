# HTTP Tool

一个轻量级的 Python CLI HTTP 请求工具，基于 urllib 标准库，无需外部依赖。

## 特性

- 🚀 零外部依赖（Python 3 标准库）
- ⚡ 简单易用的命令行接口
- 📦 支持 GET/POST/PUT/DELETE 方法
- 📋 支持自定义请求头
- 📝 支持请求体
- 💾 JSON 响应自动格式化

## 安装

无需安装，直接使用：

```bash
cd /path/to/http-tool
python http_tool.py <method> <url> [options]
```

## 使用方法

### 基本语法

```bash
python http_tool.py <method> <url> [options]
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `<method>` | HTTP 方法，可选值: GET, POST, PUT, DELETE |
| `<url>` | 目标 URL（必须） |

### 选项

| 选项 | 说明 |
|------|------|
| `-H header: value` | 添加 HTTP 请求头，可重复使用 |
| `-d body` | 设置请求体（body） |

## 使用示例

### GET 请求

```bash
# 简单 GET 请求
python http_tool.py GET https://api.example.com/users

# 带请求头
python http_tool.py GET https://api.example.com/users -H "Authorization: Bearer token123"
```

### POST 请求

```bash
# 发送 JSON 数据
python http_tool.py POST https://api.example.com/users -d '{"name":"张三","email":"zhangsan@example.com"}'
```

### PUT 请求

```bash
# 更新资源
python http_tool.py PUT https://api.example.com/users/1 -d '{"name":"李四"}' -H "Content-Type: application/json"
```

### DELETE 请求

```bash
# 删除资源
python http_tool.py DELETE https://api.example.com/users/1
```

## 输出示例

```
$ python http_tool.py GET https://jsonplaceholder.typicode.com/users/1

状态码: 200
响应内容:
{
  "id": 1,
  "name": "Leanne Graham",
  "username": "Bret",
  "email": "Sincere@april.biz"
}
```

## 常见问题

### Q: 如何发送 Form 表单数据？
A: 设置 `Content-Type: application/x-www-form-urlencoded` 请求头：
```bash
python http_tool.py POST https://example.com/form -d "username=admin&password=123" -H "Content-Type: application/x-www-form-urlencoded"
```

### Q: 如何查看完整响应头？
A: 当前版本仅显示状态码和响应体，后续版本可能支持。

## 技术栈

- Python 3.x
- urllib（标准库）

## 项目结构

```
http-tool/
├── http_tool.py      # 主程序
├── SPEC.md           # 规格说明书
└── README.md         # 使用说明
```

## License

MIT
