# -*- mode: python ; coding: utf-8 -*-
"""
Windows平台PyInstaller打包配置文件
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# 导入打包配置
from packaging.pyinstaller_hooks import (
    get_analysis_options, 
    get_exe_options,
    get_data_files
)
from packaging.resource_bundler import bundle_resources

# 配置项目路径
project_path = str(project_root)
main_script = str(project_root / "main.py")

# 获取数据文件
datas = bundle_resources(project_path)

# 隐藏导入模块
hiddenimports = [
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
    
    # 项目模块
    'src',
    'src.config',
    'src.config.config_loader',
    'src.config.config_validator',
    'src.config.default_config',
    'src.packaging',
    'src.code_searcher',
    'src.database',
    'src.search_template',
    'src.strategies',
    'src.validators',
    'src.exporter',
]

# 排除的模块
excludes = [
    'pytest',
    'unittest',
    'test',
    'tests',
    'pip',
    'setuptools',
    'wheel',
    'distutils',
    'pdb',
    'ipdb',
    'debugpy',
    'sphinx',
    'docutils',
    'jupyter',
    'ipython',
    'notebook',
    'tkinter',
    'matplotlib',
    'pyplot',
    'requests',
    'urllib3',
    'http',
    'email',
    'numpy',
    'scipy',
    'sklearn',
]

# Analysis配置
a = Analysis(
    [main_script],
    pathex=[project_path],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ配置
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE配置 - Windows单文件模式
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='hello-scan-code',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以在这里添加图标文件路径
)