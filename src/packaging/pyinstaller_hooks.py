"""
PyInstaller钩子模块

提供PyInstaller打包时需要的隐藏导入和钩子目录
"""

import os
import sys
from typing import List, Dict, Any
from pathlib import Path


def get_hidden_imports() -> List[str]:
    """
    获取PyInstaller需要的隐藏导入模块列表
    
    Returns:
        List[str]: 隐藏导入模块列表
    """
    hidden_imports = [
        # SQLAlchemy相关
        'sqlalchemy',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.sql',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.pool',
        'sqlalchemy.engine',
        
        # Alembic相关  
        'alembic',
        'alembic.runtime.migration',
        'alembic.operations',
        'alembic.script',
        
        # pandas和Excel导出相关
        'pandas',
        'pandas.io.excel',
        'openpyxl',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        'openpyxl.styles',
        
        # loguru日志相关
        'loguru',
        
        # JSON处理
        'json',
        
        # 正则表达式
        're',
        
        # 文件系统操作
        'pathlib',
        'os',
        'os.path',
        
        # 并发处理
        'concurrent.futures',
        'threading',
        'multiprocessing',
        
        # 数据结构
        'dataclasses',
        'typing',
        'collections',
        
        # 时间处理
        'datetime',
        
        # 编码相关
        'chardet',
        
        # 系统相关
        'sys',
        'platform',
    ]
    
    return hidden_imports


def get_hook_dirs() -> List[str]:
    """
    获取PyInstaller钩子目录列表
    
    Returns:
        List[str]: 钩子目录列表
    """
    current_dir = Path(__file__).parent
    hooks_dir = current_dir / "hooks"
    
    if hooks_dir.exists():
        return [str(hooks_dir)]
    return []


def get_data_files() -> List[tuple]:
    """
    获取需要打包的数据文件列表
    
    Returns:
        List[tuple]: 数据文件列表，格式为[(source, destination), ...]
    """
    data_files = []
    
    # 项目根目录
    project_root = Path(__file__).parent.parent.parent
    
    # 配置模板文件
    config_dir = project_root / "config"
    if config_dir.exists():
        template_file = config_dir / "config.template.json"
        default_file = config_dir / "default.json"
        
        if template_file.exists():
            data_files.append((str(template_file), "config.template.json"))
        if default_file.exists():
            data_files.append((str(default_file), "config/default.json"))
    
    # 数据库迁移文件（如果存在）
    migrations_dir = project_root / "src" / "database" / "migrations"
    if migrations_dir.exists():
        for migration_file in migrations_dir.glob("*.py"):
            if migration_file.name != "__init__.py":
                data_files.append((str(migration_file), f"database/migrations/{migration_file.name}"))
    
    return data_files


def get_exclude_modules() -> List[str]:
    """
    获取需要排除的模块列表
    
    Returns:
        List[str]: 排除的模块列表
    """
    exclude_modules = [
        # 测试相关模块
        'pytest',
        'unittest',
        'test',
        'tests',
        
        # 开发工具
        'pip',
        'setuptools',
        'wheel',
        'distutils',
        
        # 调试工具
        'pdb',
        'ipdb',
        'debugpy',
        
        # 文档工具
        'sphinx',
        'docutils',
        
        # Jupyter相关
        'jupyter',
        'ipython',
        'notebook',
        
        # IDE相关
        'pylsp',
        'pyls',
        
        # 不需要的GUI库
        'tkinter',
        'matplotlib',
        'pyplot',
        
        # 不需要的网络库
        'requests',
        'urllib3',
        'http',
        'email',
        
        # 不需要的科学计算库
        'numpy',
        'scipy',
        'sklearn',
    ]
    
    return exclude_modules


def get_collect_submodules() -> List[str]:
    """
    获取需要收集所有子模块的包列表
    
    Returns:
        List[str]: 包列表
    """
    return [
        'sqlalchemy',
        'alembic',
        'pandas',
        'openpyxl',
        'loguru',
    ]


def create_spec_options() -> Dict[str, Any]:
    """
    创建PyInstaller .spec文件的选项字典
    
    Returns:
        Dict[str, Any]: spec文件选项
    """
    options = {
        'hiddenimports': get_hidden_imports(),
        'excludes': get_exclude_modules(),
        'datas': get_data_files(),
        'collect_submodules': get_collect_submodules(),
        'noarchive': False,
        'optimize': 2,
        'strip': False,
        'upx': True,
        'upx_exclude': [],
        'runtime_tmpdir': None,
        'console': True,
        'disable_windowed_traceback': False,
        'target_arch': None,
        'codesign_identity': None,
        'entitlements_file': None,
    }
    
    return options


def get_analysis_options() -> Dict[str, Any]:
    """
    获取Analysis阶段的选项
    
    Returns:
        Dict[str, Any]: Analysis选项
    """
    return {
        'pathex': [],
        'binaries': [],
        'datas': get_data_files(),
        'hiddenimports': get_hidden_imports(),
        'hookspath': get_hook_dirs(),
        'hooksconfig': {},
        'runtime_hooks': [],
        'excludes': get_exclude_modules(),
        'win_no_prefer_redirects': False,
        'win_private_assemblies': False,
        'cipher': None,
        'noarchive': False,
    }


def get_exe_options(name: str = "hello-scan-code") -> Dict[str, Any]:
    """
    获取EXE阶段的选项
    
    Args:
        name: 可执行文件名称
        
    Returns:
        Dict[str, Any]: EXE选项
    """
    return {
        'name': name,
        'debug': False,
        'bootloader_ignore_signals': False,
        'strip': False,
        'upx': True,
        'upx_exclude': [],
        'runtime_tmpdir': None,
        'console': True,
        'disable_windowed_traceback': False,
        'target_arch': None,
        'codesign_identity': None,
        'entitlements_file': None,
        'icon': None,  # 可以在这里指定图标文件路径
    }