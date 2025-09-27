"""
数据库操作模块 - 兼容性封装

为了保持向后兼容，这个文件保留了原有的导入路径，
但内部实现已经切换到新的ORM架构。

新的数据库架构位于 src/database/ 目录下。
"""

# 从新的数据库模块导入兼容性适配器
from .database import DatabaseManager

# 保持向后兼容，导出相同的接口
__all__ = ['DatabaseManager']