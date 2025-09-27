"""
PyInstaller钩子 - pandas支持

确保pandas相关模块正确打包
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集pandas数据文件
datas = collect_data_files('pandas')

# 收集pandas隐式导入
hiddenimports = [
    'pandas._libs.tslib',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.skiplist',
    'pandas.io.formats.style',
    'pandas._libs.writers'
]