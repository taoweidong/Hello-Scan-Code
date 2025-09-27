"""
日志配置管理

提供统一的日志配置和设置功能
"""

import sys
import os
from dataclasses import dataclass
from typing import Optional
from loguru import logger
from .base_config import BaseConfig


@dataclass
class LoggerConfig(BaseConfig):
    """日志配置类"""
    
    # 日志级别和输出配置
    log_level: str = "INFO"
    log_file_path: str = "logs/code_search_{time:YYYY-MM-DD}.log"
    log_rotation: str = "500 MB"
    log_retention: str = "10 days"
    console_output: bool = True
    
    # 日志格式配置
    file_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    console_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    
    def load_from_env(self) -> None:
        """从环境变量加载配置"""
        self.log_level = self.get_env_var('LOG_LEVEL', self.log_level)
        self.log_file_path = self.get_env_var('LOG_FILE_PATH', self.log_file_path)
        self.log_rotation = self.get_env_var('LOG_ROTATION', self.log_rotation)
        self.log_retention = self.get_env_var('LOG_RETENTION', self.log_retention)
        self.console_output = self.get_env_var('CONSOLE_OUTPUT', self.console_output, bool)
        self.file_format = self.get_env_var('LOG_FILE_FORMAT', self.file_format)
        self.console_format = self.get_env_var('LOG_CONSOLE_FORMAT', self.console_format)
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
        return self.log_level.upper() in valid_levels
    
    def setup_logger(self) -> None:
        """设置日志系统"""
        # 移除默认的日志处理器
        logger.remove()
        
        # 确保日志目录存在
        if self.log_file_path:
            log_dir = os.path.dirname(self.log_file_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # 添加文件日志处理器
            logger.add(
                self.log_file_path,
                rotation=self.log_rotation,
                retention=self.log_retention,
                level=self.log_level,
                encoding="utf-8",
                format=self.file_format
            )
        
        # 添加控制台输出
        if self.console_output:
            logger.add(
                sys.stderr,
                level=self.log_level,
                format=self.console_format
            )


# 全局日志配置实例
_logger_config: Optional[LoggerConfig] = None
_logger_initialized: bool = False


def get_logger_config() -> LoggerConfig:
    """获取日志配置实例"""
    global _logger_config
    if _logger_config is None:
        _logger_config = LoggerConfig()
        _logger_config.load_from_env()
    return _logger_config


def setup_logger(config: Optional[LoggerConfig] = None) -> None:
    """设置全局日志系统"""
    global _logger_initialized
    
    if config is None:
        config = get_logger_config()
    
    if not _logger_initialized:
        config.setup_logger()
        _logger_initialized = True


def get_logger():
    """
    获取配置好的logger实例
    保持向后兼容性
    """
    global _logger_initialized
    
    if not _logger_initialized:
        setup_logger()
    
    return logger