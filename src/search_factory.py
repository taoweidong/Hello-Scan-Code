#!/usr/bin/env python3
"""
搜索策略工厂
使用工厂模式创建不同的搜索策略
"""

from typing import Optional
from .strategies import SearchStrategy, GrepSearchStrategy, PythonSearchStrategy
from .logger_config import get_logger

logger = get_logger()


class SearchStrategyFactory:
    """搜索策略工厂类"""
    
    @staticmethod
    def create_strategy(strategy_type: str) -> Optional[SearchStrategy]:
        """
        根据策略类型创建搜索策略
        
        Args:
            strategy_type: 策略类型 ('grep' 或 'python')
            
        Returns:
            搜索策略实例或None
        """
        if strategy_type.lower() == 'grep':
            logger.info("创建Grep搜索策略")
            return GrepSearchStrategy()
        elif strategy_type.lower() == 'python':
            logger.info("创建Python搜索策略")
            return PythonSearchStrategy()
        else:
            logger.warning(f"未知的搜索策略类型: {strategy_type}")
            return None
    
    @staticmethod
    def create_default_strategy() -> SearchStrategy:
        """
        创建默认搜索策略（Grep策略）
        
        Returns:
            默认搜索策略实例
        """
        logger.info("创建默认搜索策略（Grep）")
        return GrepSearchStrategy()