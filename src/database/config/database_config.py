"""
数据库配置类

管理数据库连接参数和性能调优配置
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """
    数据库连接配置类
    
    集中管理所有数据库相关的配置参数
    """
    
    # 数据库文件路径
    db_path: str
    
    # 连接池配置
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    
    # SQLite特定配置
    sqlite_timeout: float = 20.0
    sqlite_check_same_thread: bool = False
    
    # 性能优化配置
    echo: bool = False  # 是否输出SQL语句
    echo_pool: bool = False  # 是否输出连接池信息
    
    # 事务配置
    autocommit: bool = False
    autoflush: bool = True
    
    def __post_init__(self):
        """
        初始化后的验证和设置
        """
        # 确保数据库目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    @property
    def database_url(self) -> str:
        """
        构建数据库连接URL
        
        Returns:
            SQLAlchemy格式的数据库连接URL
        """
        # 使用绝对路径确保路径正确
        abs_path = os.path.abspath(self.db_path)
        return f"sqlite:///{abs_path}"
    
    def get_engine_kwargs(self) -> Dict[str, Any]:
        """
        获取创建数据库引擎的参数
        
        Returns:
            引擎参数字典
        """
        kwargs = {
            'echo': self.echo,
            'echo_pool': self.echo_pool,
        }
        
        # 仅在非SQLite数据库中添加连接池参数
        if not self.database_url.startswith('sqlite'):
            kwargs.update({
                'pool_pre_ping': self.pool_pre_ping,
                'pool_recycle': self.pool_recycle,
            })
        
        return kwargs
    
    def get_session_kwargs(self) -> Dict[str, Any]:
        """
        获取创建会话的参数
        
        Returns:
            会话参数字典
        """
        return {
            'autocommit': self.autocommit,
            'autoflush': self.autoflush,
        }
    
    @classmethod
    def from_env(cls, db_path: Optional[str] = None) -> 'DatabaseConfig':
        """
        从环境变量创建配置实例
        
        Args:
            db_path: 数据库路径，如果为None则从环境变量读取
            
        Returns:
            配置实例
        """
        if db_path is None:
            db_path = os.getenv('DB_PATH', 'db/search_results.db')
        
        return cls(
            db_path=db_path,
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30')),
            pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '3600')),
            pool_pre_ping=os.getenv('DB_POOL_PRE_PING', 'true').lower() == 'true',
            sqlite_timeout=float(os.getenv('DB_SQLITE_TIMEOUT', '20.0')),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true',
            echo_pool=os.getenv('DB_ECHO_POOL', 'false').lower() == 'true',
        )
    
    @classmethod
    def for_testing(cls, db_path: str = ':memory:') -> 'DatabaseConfig':
        """
        创建用于测试的配置实例
        
        Args:
            db_path: 测试数据库路径，默认使用内存数据库
            
        Returns:
            测试配置实例
        """
        return cls(
            db_path=db_path,
            pool_size=1,
            max_overflow=0,
            pool_timeout=5,
            echo=True,  # 测试时启用SQL输出
            sqlite_check_same_thread=False  # 测试时允许多线程访问
        )