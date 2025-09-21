#!/usr/bin/env python3
"""
结果验证装饰器
使用装饰器模式处理结果验证功能
"""

from typing import List, Dict, Any
from abc import ABC, abstractmethod
from .logger_config import get_logger

logger = get_logger()


class ResultValidator(ABC):
    """结果验证器抽象基类"""
    
    @abstractmethod
    def validate(self, file_results: List[Dict[str, Any]], search_terms: List[str] | str, is_regex: bool) -> List[Dict[str, Any]]:
        """
        验证搜索结果的抽象方法
        
        Args:
            file_results: 文件搜索结果
            search_terms: 搜索词列表或单个搜索词
            is_regex: 是否使用正则表达式
            
        Returns:
            验证后的结果
        """
        pass


class ParallelResultValidator(ResultValidator):
    """并行结果验证器"""
    
    def __init__(self, max_workers: int = 4):
        """
        初始化并行结果验证器
        
        Args:
            max_workers: 最大工作进程数
        """
        self.max_workers = max_workers
    
    def validate(self, file_results: List[Dict[str, Any]], search_terms: List[str] | str, is_regex: bool) -> List[Dict[str, Any]]:
        """
        并行验证搜索结果
        """
        from .searcher import parallel_validate
        logger.info(f"启用并行验证，使用 {self.max_workers} 个工作进程")
        return parallel_validate(file_results, search_terms, is_regex, self.max_workers)