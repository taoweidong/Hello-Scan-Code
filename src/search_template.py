#!/usr/bin/env python3
"""
搜索模板方法
使用模板方法模式定义搜索流程的通用结构
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .config import SearchConfig
from .strategies import SearchStrategy
from .search_factory import SearchStrategyFactory
from .logger_config import get_logger

logger = get_logger()


class SearchTemplate(ABC):
    """搜索模板抽象类"""
    
    def __init__(self, config: SearchConfig):
        """
        初始化搜索模板
        
        Args:
            config: 搜索配置
        """
        self.config = config
        self.strategy = self._create_search_strategy()
    
    def search(self) -> List[Dict[str, Any]]:
        """
        搜索模板方法，定义搜索流程
        
        Returns:
            搜索结果列表
        """
        logger.info(f"开始搜索: {self.config.search_term}")
        logger.info(f"仓库路径: {self.config.repo_path}")
        logger.info(f"是否正则表达式: {self.config.is_regex}")
        
        # 解析搜索词
        search_terms = self._parse_search_terms()
        
        # 执行初步搜索
        matched_results = self._perform_initial_search(search_terms)
        
        if not matched_results:
            logger.info("未找到匹配的文件")
            return []
        
        total_matches = sum(len(item['matches']) for item in matched_results)
        logger.info(f"初步搜索找到 {len(matched_results)} 个文件，共 {total_matches} 个匹配行")
        
        # 如果启用二次校验
        if self.config.validate:
            matched_results = self._perform_validation(matched_results, search_terms)
            
            if not matched_results:
                logger.info("二次校验后未找到匹配的文件")
                return []
            
            total_matches = sum(len(item['matches']) for item in matched_results)
            logger.info(f"二次校验后找到 {len(matched_results)} 个匹配文件，共 {total_matches} 个匹配行")
        
        return matched_results
    
    def _parse_search_terms(self) -> List[str] | str:
        """
        解析搜索词
        
        Returns:
            搜索词列表或单个搜索词
        """
        return self.config.search_term.split(',') if ',' in self.config.search_term else self.config.search_term
    
    def _perform_initial_search(self, search_terms: List[str] | str) -> List[Dict[str, Any]]:
        """
        执行初步搜索（模板方法的具体步骤）
        
        Args:
            search_terms: 搜索词列表或单个搜索词
            
        Returns:
            初步搜索结果
        """
        return self.strategy.search(self.config.repo_path, search_terms, self.config.is_regex)
    
    @abstractmethod
    def _perform_validation(self, matched_results: List[Dict[str, Any]], search_terms: List[str] | str) -> List[Dict[str, Any]]:
        """
        执行二次校验（子类必须实现）
        
        Args:
            matched_results: 初步搜索结果
            search_terms: 搜索词列表或单个搜索词
            
        Returns:
            校验后的结果
        """
        pass
    
    @abstractmethod
    def _create_search_strategy(self) -> SearchStrategy:
        """
        创建搜索策略（子类必须实现）
        
        Returns:
            搜索策略实例
        """
        pass


class DefaultSearchTemplate(SearchTemplate):
    """默认搜索模板实现"""
    
    def _perform_validation(self, matched_results: List[Dict[str, Any]], search_terms: List[str] | str) -> List[Dict[str, Any]]:
        """
        执行二次校验（使用默认验证方法）
        """
        from .searcher import parallel_validate
        logger.info(f"启用二次校验，使用 {self.config.validate_workers} 个工作进程")
        return parallel_validate(
            matched_results, 
            search_terms, 
            self.config.is_regex, 
            self.config.validate_workers
        )
    
    def _create_search_strategy(self) -> SearchStrategy:
        """
        创建默认搜索策略
        """
        return SearchStrategyFactory.create_default_strategy()