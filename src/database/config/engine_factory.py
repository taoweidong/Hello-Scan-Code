"""
数据库引擎工厂

负责创建和管理SQLAlchemy数据库引擎实例
"""

import sqlite3
from typing import Optional
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.pool import StaticPool
from .database_config import DatabaseConfig
from ..logger_config import get_logger

logger = get_logger()


class EngineFactory:
    """
    数据库引擎工厂类
    
    负责根据配置创建合适的数据库引擎，并进行性能优化设置
    """
    
    _instance: Optional['EngineFactory'] = None
    _engines: dict = {}
    
    def __new__(cls) -> 'EngineFactory':
        """
        单例模式实现
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def create_engine(cls, config: DatabaseConfig) -> Engine:
        """
        根据配置创建数据库引擎
        
        Args:
            config: 数据库配置实例
            
        Returns:
            配置好的SQLAlchemy引擎
        """
        # 检查是否已有相同配置的引擎
        cache_key = config.database_url
        if cache_key in cls._engines:
            logger.info(f"重用已有数据库引擎: {cache_key}")
            return cls._engines[cache_key]
        
        try:
            # 获取引擎参数
            engine_kwargs = config.get_engine_kwargs()
            
            # 为SQLite添加特殊处理
            if config.database_url.startswith('sqlite'):
                # SQLite不支持连接池参数，移除这些参数
                engine_kwargs.pop('pool_pre_ping', None)
                engine_kwargs.pop('pool_recycle', None)
                engine_kwargs.update({
                    'poolclass': StaticPool,
                    'connect_args': {
                        'timeout': config.sqlite_timeout,
                        'check_same_thread': config.sqlite_check_same_thread,
                    }
                })
            
            # 创建引擎
            engine = create_engine(config.database_url, **engine_kwargs)
            
            # 为SQLite配置性能优化
            if config.database_url.startswith('sqlite'):
                cls._configure_sqlite_optimization(engine)
            
            # 缓存引擎
            cls._engines[cache_key] = engine
            
            logger.info(f"成功创建数据库引擎: {config.database_url}")
            return engine
            
        except Exception as e:
            logger.error(f"创建数据库引擎失败: {e}")
            raise
    
    @staticmethod
    def _configure_sqlite_optimization(engine: Engine) -> None:
        """
        配置SQLite性能优化参数
        
        Args:
            engine: SQLite引擎实例
        """
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """
            设置SQLite性能优化参数
            """
            cursor = dbapi_connection.cursor()
            
            # 启用WAL模式以提升并发性能
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # 设置同步模式为NORMAL以平衡性能和安全性
            cursor.execute("PRAGMA synchronous=NORMAL")
            
            # 增加缓存大小（单位：页，每页通常4KB）
            cursor.execute("PRAGMA cache_size=10000")
            
            # 设置临时存储为内存模式
            cursor.execute("PRAGMA temp_store=memory")
            
            # 启用内存映射I/O
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            # 设置页面大小为4KB（默认值，明确设置）
            cursor.execute("PRAGMA page_size=4096")
            
            # 启用外键约束
            cursor.execute("PRAGMA foreign_keys=ON")
            
            cursor.close()
            
            logger.debug("SQLite性能优化参数设置完成")
    
    @classmethod
    def get_engine(cls, config: DatabaseConfig) -> Engine:
        """
        获取数据库引擎（如果不存在则创建）
        
        Args:
            config: 数据库配置实例
            
        Returns:
            数据库引擎
        """
        return cls.create_engine(config)
    
    @classmethod
    def close_all_engines(cls) -> None:
        """
        关闭所有缓存的数据库引擎
        """
        for url, engine in cls._engines.items():
            try:
                engine.dispose()
                logger.info(f"关闭数据库引擎: {url}")
            except Exception as e:
                logger.error(f"关闭引擎失败 {url}: {e}")
        
        cls._engines.clear()
    
    @classmethod
    def reset(cls) -> None:
        """
        重置工厂状态（主要用于测试）
        """
        cls.close_all_engines()
        cls._instance = None
    
    def __del__(self):
        """
        析构函数，确保引擎正确关闭
        """
        self.close_all_engines()