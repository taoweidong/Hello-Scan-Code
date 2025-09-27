"""
PyInstaller钩子 - loguru支持

确保loguru日志系统正确打包
"""

from PyInstaller.utils.hooks import collect_data_files

# 收集loguru数据文件
datas = collect_data_files('loguru')

# loguru隐式导入
hiddenimports = [
    'loguru._defaults',
    'loguru._colorama',
]