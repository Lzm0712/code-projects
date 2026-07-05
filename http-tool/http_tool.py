#!/usr/bin/env python3
"""
HTTP Tool - CLI HTTP 请求工具
通过命令行发送 HTTP 请求并展示格式化响应
"""

import sys
import json
import argparse
from urllib import request
from urllib.error import URLError, HTTPError


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='HTTP Tool - CLI HTTP 请求工具',
        usage='python http_tool.py <method> <url> [options]'
    )
    
    parser.add_argument(
        'method',
        choices=['GET', 'POST', 'PUT', 'DELETE'],
        help='HTTP 方法'
    )
    
    parser.add_argument(
        'url',
        help='请求 URL'
    )
    
    parser.add_argument(
        '-H',
        action='append',
        dest='headers',
        metavar='header: value',
        help='添加 HTTP 请求头，可重复使用'
    )
    
    parser.add_argument(
        '-d',
        dest='body',
        metavar='body',
        help='设置请求体'
    )
    
    return parser.parse_args()


def parse_headers(headers_list):
    """解析 headers 列表为字典"""
    if not headers_list:
        return {}
    
    headers_dict = {}
    for header in headers_list:
        if ':' in header:
            key, value = header.split(':', 1)
            headers_dict[key.strip()] = value.strip()
    return headers_dict


def format_response(response):
    """格式化响应输出"""
    # 获取状态码
    status_code = response.status
    
    # 读取响应内容
    content = response.read()
    
    # 尝试解析 JSON
    try:
        json_data = json.loads(content.decode('utf-8'))
        formatted_body = json.dumps(json_data, indent=2, ensure_ascii=False)
        print(f"Status: {status_code}")
        print("Content-Type: application/json")
        print("\n--- Response Body (JSON) ---\n")
        print(formatted_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # 非 JSON 响应直接输出
        print(f"Status: {status_code}")
        print("\n--- Response Body ---\n")
        if content:
            try:
                print(content.decode('utf-8'))
            except UnicodeDecodeError:
                print(content.decode('latin-1'))


def send_request(method, url, headers=None, body=None):
    """发送 HTTP 请求"""
    try:
        # 构建请求
        req = request.Request(
            url,
            method=method,
            headers=headers or {},
            data=body.encode('utf-8') if body else None
        )
        
        # 发送请求并获取响应
        with request.urlopen(req) as response:
            format_response(response)
            
    except HTTPError as e:
        # HTTP 错误（如 404、500 等）
        print(f"HTTP Error: {e.code} {e.reason}", file=sys.stderr)
        # 尝试读取响应体
        if e.fp:
            content = e.fp.read()
            try:
                json_data = json.loads(content.decode('utf-8'))
                print("\n--- Error Response Body (JSON) ---\n")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
            except (json.JSONDecodeError, UnicodeDecodeError):
                print("\n--- Error Response Body ---\n")
                print(content.decode('utf-8', errors='replace'))
        sys.exit(1)
        
    except URLError as e:
        # URL 错误或网络错误
        print(f"Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        # 其他错误
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """主函数"""
    args = parse_args()
    
    # 解析 headers
    headers = parse_headers(args.headers)
    
    # 发送请求
    send_request(
        method=args.method,
        url=args.url,
        headers=headers,
        body=args.body
    )


if __name__ == '__main__':
    main()
