"""语言定义与扩展名映射"""

# 支持的语言及其扩展名
LANGUAGE_EXTENSIONS = {
    'Python': ['.py'],
    'JavaScript': ['.js'],
    'TypeScript': ['.ts'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'JSON': ['.json'],
    'YAML': ['.yaml', '.yml'],
    'Markdown': ['.md'],
}

# 扩展名到语言的映射
EXT_TO_LANG = {}
for lang, exts in LANGUAGE_EXTENSIONS.items():
    for ext in exts:
        EXT_TO_LANG[ext] = lang

# 语言的注释风格
COMMENT_STYLES = {
    'Python': {
        'single': '#',
        'multi_start': ['"""', "'''"],
        'multi_end': ['"""', "'''"],
    },
    'JavaScript': {
        'single': '//',
        'multi_start': ['/*'],
        'multi_end': ['*/'],
    },
    'TypeScript': {
        'single': '//',
        'multi_start': ['/*'],
        'multi_end': ['*/'],
    },
    'Go': {
        'single': '//',
        'multi_start': ['/*'],
        'multi_end': ['*/'],
    },
    'Rust': {
        'single': '//',
        'multi_start': ['/*'],
        'multi_end': ['*/'],
    },
    'JSON': {
        'single': None,
        'multi_start': [],
        'multi_end': [],
    },
    'YAML': {
        'single': '#',
        'multi_start': [],
        'multi_end': [],
    },
    'Markdown': {
        'single': '#',
        'multi_start': ['<!--'],
        'multi_end': ['-->'],
    },
}

# 需要跳过的目录
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', 'venv', 'env',
    '.svn', '.hg', 'dist', 'build', '.idea', '.vscode',
    'vendor', 'target', 'bin', 'obj',
}


def get_language(filename: str) -> str | None:
    """根据文件名获取语言类型"""
    for ext in EXT_TO_LANG:
        if filename.endswith(ext):
            return EXT_TO_LANG[ext]
    return None


def get_comment_style(language: str) -> dict | None:
    """获取语言的注释风格"""
    return COMMENT_STYLES.get(language)
