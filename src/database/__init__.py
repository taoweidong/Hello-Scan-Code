"""
数据库模块 - 提供基于SQLAlchemy的数据访问层

本模块包含：
- 数据模型定义
- 数据库会话管理
- 数据访问仓库
- 数据库迁移服务
- 兼容性适配器
"""

from .session_manager import SessionManager
from .models import SearchResultModel, BaseModel
from .repositories import SearchResultRepository
from .migrations import MigrationService
from .compatibility import DatabaseManager  # 兼容性适配器
from .config import DatabaseConfig, EngineFactory

__all__ = [
    'SessionManager',
    'SearchResultModel',
    'BaseModel', 
    'SearchResultRepository',
    'MigrationService',
    'DatabaseManager',  # 保持向后兼容
    'DatabaseConfig',
    'EngineFactory'
]