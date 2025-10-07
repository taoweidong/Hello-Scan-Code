# -*- mode: python ; coding: utf-8 -*-
"""
Windows平台PyInstaller打包配置文件 - 适配新架构
"""

import sys
import os
from pathlib import Path

# 配置项目路径（使用绝对路径避免__file__问题）
project_root = Path(r"E:\GitHub\Hello-Scan-Code").resolve()
sys.path.insert(0, str(project_root))

# 导入新架构的打包配置
try:
    from src.packaging.pyinstaller_hooks import (
        get_analysis_options, 
        get_exe_options,
        get_data_files,
        get_hidden_imports,
        get_exclude_modules
    )
    from src.packaging.resource_bundler import bundle_resources
except ImportError:
    # 如果导入失败，使用默认配置
    def get_hidden_imports():
        return []
    
    def get_exclude_modules():
        return []
    
    def bundle_resources(project_path):
        return []

# 配置项目路径
project_path = str(project_root)
main_script = str(project_root / "src" / "main.py")  # 修改为src/main.py

# 获取数据文件和资源
try:
    datas = bundle_resources(project_path)
except:
    datas = []

# 隐藏导入模块（包含新架构的配置模块）
try:
    hiddenimports = get_hidden_imports()
except:
    hiddenimports = []

# 排除的模块
try:
    excludes = get_exclude_modules()
except:
    excludes = []

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