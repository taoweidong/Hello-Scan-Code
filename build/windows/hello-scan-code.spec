# -*- mode: python ; coding: utf-8 -*-
<<<<<<< HEAD

block_cipher = None

a = Analysis(
    [r'E:\GitHub\Hello-Scan-Code\main.py'],
    pathex=[r'E:\GitHub\Hello-Scan-Code'],
    binaries=[],
    datas=[
        (r'E:\GitHub\Hello-Scan-Code\config\config.schema.json', 'config/'),
        (r'E:\GitHub\Hello-Scan-Code\config\config.template.json', 'config/'),
        (r'E:\GitHub\Hello-Scan-Code\config\default.json', 'config/'),
        (r'E:\GitHub\Hello-Scan-Code\config\template_test.json', 'config/'),
        (r'E:\GitHub\Hello-Scan-Code\src\database\migrations\migration_service.py', 'database\migrations/'),
        (r'E:\GitHub\Hello-Scan-Code\src\database\migrations\__init__.py', 'database\migrations/')
    ],
    hiddenimports=[
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.engine.strategies',
        'pandas._libs.writers',
        'pandas.io.formats.style',
        'openpyxl.compat',
        'openpyxl.writer.excel',
        'loguru._defaults',
        'loguru._colorama',
        'jsonschema.validators',
        'jsonschema._format'
    ],
    hookspath=[r'E:\GitHub\Hello-Scan-Code\src\packaging\hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

=======
"""
Windows平台PyInstaller打包配置文件 - 适配新架构
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入新架构的打包配置
from src.packaging.pyinstaller_hooks import (
    get_analysis_options, 
    get_exe_options,
    get_data_files,
    get_hidden_imports,
    get_exclude_modules
)
from src.packaging.resource_bundler import bundle_resources

# 配置项目路径
project_path = str(project_root)
main_script = str(project_root / "main.py")

# 获取数据文件和资源
datas = bundle_resources(project_path)

# 隐藏导入模块（包含新架构的配置模块）
hiddenimports = get_hidden_imports()

# 排除的模块
excludes = get_exclude_modules()

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
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
<<<<<<< HEAD
    name='hello-scan-code.exe',
=======
    name='hello-scan-code',
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
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
<<<<<<< HEAD
    icon=None
)


=======
    icon=None,  # 可以在这里添加图标文件路径
)
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
