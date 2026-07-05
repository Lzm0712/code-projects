#!/usr/bin/env python3
"""
fsearch - CLI 文件搜索工具
按名称、内容、类型搜索文件，支持正则表达式
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Optional


# 二进制文件判断（根据字节码判断）
BINARY_BYTES = bytes(range(128, 256))


def is_binary_file(file_path: Path) -> bool:
    """判断文件是否为二进制文件"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            return BINARY_BYTES[:len(chunk)] == chunk or any(b > 127 for b in chunk)
    except (OSError, PermissionError):
        return True


def search_by_name(pattern: str, path: Path, recursive: bool, verbose: bool) -> List[Path]:
    """按文件名搜索"""
    results = []
    compiled_pattern = re.compile(pattern)
    
    try:
        if recursive:
            files = path.rglob('*')
        else:
            files = path.glob('*')
        
        for file_path in files:
            if file_path.is_file() and compiled_pattern.search(file_path.name):
                results.append(file_path.resolve())
                if verbose:
                    print(f"[MATCH] {file_path}", file=sys.stderr)
    except PermissionError:
        if verbose:
            print(f"[SKIP] Permission denied: {path}", file=sys.stderr)
    
    return results


def search_by_content(pattern: str, path: Path, recursive: bool, verbose: bool) -> List[Path]:
    """按文件内容搜索"""
    results = []
    compiled_pattern = re.compile(pattern)
    MAX_READ_SIZE = 1024 * 1024  # 1MB
    
    try:
        if recursive:
            files = path.rglob('*')
        else:
            files = path.glob('*')
        
        for file_path in files:
            if not file_path.is_file():
                continue
            
            if is_binary_file(file_path):
                if verbose:
                    print(f"[SKIP] Binary file: {file_path}", file=sys.stderr)
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(MAX_READ_SIZE)
                    if compiled_pattern.search(content):
                        results.append(file_path.resolve())
                        if verbose:
                            print(f"[MATCH] {file_path}", file=sys.stderr)
            except (OSError, PermissionError):
                if verbose:
                    print(f"[SKIP] Cannot read: {file_path}", file=sys.stderr)
                continue
    except PermissionError:
        if verbose:
            print(f"[SKIP] Permission denied: {path}", file=sys.stderr)
    
    return results


def search_by_type(extensions: str, path: Path, recursive: bool, verbose: bool) -> List[Path]:
    """按文件类型（扩展名）搜索"""
    results = []
    
    # 支持多扩展名（逗号分隔）
    ext_list = [ext.strip().lstrip('.') for ext in extensions.split(',') if ext.strip()]
    
    if not ext_list:
        print("Error: Extension cannot be empty", file=sys.stderr)
        sys.exit(1)
    
    try:
        for ext in ext_list:
            pattern = f"*.{ext}"
            if recursive:
                files = path.rglob(pattern)
            else:
                files = path.glob(pattern)
            
            for file_path in files:
                if file_path.is_file():
                    results.append(file_path.resolve())
                    if verbose:
                        print(f"[MATCH] {file_path}", file=sys.stderr)
    except PermissionError:
        if verbose:
            print(f"[SKIP] Permission denied: {path}", file=sys.stderr)
    
    return results


def validate_pattern(pattern: str) -> bool:
    """验证正则表达式是否有效"""
    try:
        re.compile(pattern)
        return True
    except re.error as e:
        print(f"Error: Invalid regex pattern '{pattern}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='fsearch',
        description='CLI 文件搜索工具 - 按名称、内容、类型搜索文件'
    )
    
    parser.add_argument(
        'command',
        choices=['name', 'content', 'type'],
        help='搜索子命令: name(按文件名), content(按内容), type(按类型)'
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default=Path.cwd(),
        type=Path,
        help='搜索起始目录 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        help='正则表达式模式 (用于 name 和 content 命令)',
        dest='pattern'
    )
    
    parser.add_argument(
        '-e', '--ext',
        help='文件扩展名，如 py, txt (用于 type 命令，支持逗号分隔多扩展名)',
        dest='ext'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='递归搜索 (默认: 开启)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help='输出详细日志'
    )
    
    args = parser.parse_args()
    
    # 验证目录是否存在
    if not args.path.exists():
        print(f"Error: Directory does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    if not args.path.is_dir():
        print(f"Error: Path is not a directory: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    results: List[Path] = []
    
    if args.command == 'name':
        if not args.pattern:
            print("Error: -p/--pattern is required for 'name' command", file=sys.stderr)
            sys.exit(1)
        validate_pattern(args.pattern)
        results = search_by_name(args.pattern, args.path, args.recursive, args.verbose)
    
    elif args.command == 'content':
        if not args.pattern:
            print("Error: -p/--pattern is required for 'content' command", file=sys.stderr)
            sys.exit(1)
        validate_pattern(args.pattern)
        results = search_by_content(args.pattern, args.path, args.recursive, args.verbose)
    
    elif args.command == 'type':
        if not args.ext:
            print("Error: -e/--ext is required for 'type' command", file=sys.stderr)
            sys.exit(1)
        results = search_by_type(args.ext, args.path, args.recursive, args.verbose)
    
    # 输出结果
    for result in sorted(results):
        print(result)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
