"""
统一配置模块

提供所有配置相关的导入接口，简化配置使用，支持JSON配置文件
"""

from .base_config import BaseConfig
from .app_config import AppConfig, parse_args, SearchConfig  # 保持向后兼容
from .logger_config import LoggerConfig, get_logger, setup_logger
from .database_config import DatabaseConfig
from .json_config_loader import (
    JsonConfigLoader, 
    get_json_loader, 
    load_config_from_json, 
    create_config_template
)
from .config_manager import (
    ConfigManager, 
    get_config_manager,
    get_app_config,
    get_logger_config, 
    get_database_config
)

__all__ = [
    # 基础配置
    'BaseConfig',
    
    # 具体配置类
    'AppConfig',
    'LoggerConfig', 
    'DatabaseConfig',
    
    # 配置管理器
    'ConfigManager',
    'get_config_manager',
    'get_app_config',
    'get_logger_config',
    'get_database_config',
    
    # JSON配置支持
    'JsonConfigLoader',
    'get_json_loader',
    'load_config_from_json',
    'create_config_template',
    
    # 日志相关
    'get_logger',
    'setup_logger',
    
    # 向后兼容
    'SearchConfig',
    'parse_args',
]

# 自动初始化配置管理器
_manager = get_config_manager()