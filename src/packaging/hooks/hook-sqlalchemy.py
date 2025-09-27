"""
PyInstaller钩子 - SQLAlchemy支持

确保SQLAlchemy相关模块正确打包
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集SQLAlchemy数据文件
datas = collect_data_files('sqlalchemy')

# 收集SQLAlchemy子模块
hiddenimports = collect_submodules('sqlalchemy.dialects')