"""
数据库模块日志配置

为数据库模块提供统一的日志记录功能
"""

import sys
from loguru import logger


def get_logger():
    """
    获取配置好的logger实例
    
    Returns:
        配置好的logger
    """
    # 移除默认的handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO"
    )
    
    return logger