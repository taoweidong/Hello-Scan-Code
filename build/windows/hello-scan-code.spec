# -*- mode: python ; coding: utf-8 -*-

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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='hello-scan-code.exe',
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
    icon=None
)


