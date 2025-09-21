#!/usr/bin/env python3
"""
高效代码搜索工具核心类
"""

import os
import sys
from typing import List, Dict, Any
from .logger_config import get_logger
from .config import SearchConfig
from .searcher import run_grep_search, parallel_validate, run_python_search
from .database import DatabaseManager
from .exporter import ExcelExporter

logger = get_logger()


class CodeSearcher:
    """代码搜索器主类，整合所有搜索功能"""
    
    def __init__(self, config: SearchConfig):
        """
        初始化代码搜索器
        
        Args:
            config: 搜索配置对象
        """
        self.config = config
        self.db_manager = DatabaseManager(config.db_path)
        self.excel_exporter = ExcelExporter(config.excel_path)
        
        # 检查仓库路径是否存在
        if not os.path.exists(config.repo_path):
            logger.error(f"仓库路径不存在: {config.repo_path}")
            raise FileNotFoundError(f"仓库路径不存在: {config.repo_path}")
    
    def search(self) -> List[Dict[str, Any]]:
        """
        执行代码搜索的主要方法
        
        Returns:
            匹配结果列表
        """
        logger.info(f"开始搜索: {self.config.search_term}")
        logger.info(f"仓库路径: {self.config.repo_path}")
        logger.info(f"是否正则表达式: {self.config.is_regex}")
        
        # 将搜索词转换为列表格式（保持向后兼容性）
        search_terms = self._parse_search_terms()
        
        # 使用grep进行初步搜索
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
    
    def save_results(self, matched_results: List[Dict[str, Any]]) -> None:
        """
        保存搜索结果
        
        Args:
            matched_results: 匹配结果列表
        """
        # 保存到数据库
        self.db_manager.save_results(matched_results)
        
        # 导出到Excel
        self.excel_exporter.export_to_excel(matched_results)
        
        logger.info("结果保存完成")
    
    def _parse_search_terms(self) -> List[str] | str:
        """
        解析搜索词
        
        Returns:
            搜索词列表或单个搜索词
        """
        return self.config.search_term.split(',') if ',' in self.config.search_term else self.config.search_term
    
    def _perform_initial_search(self, search_terms: List[str] | str) -> List[Dict[str, Any]]:
        """
        执行初步搜索
        
        Args:
            search_terms: 搜索词列表或单个搜索词
            
        Returns:
            初步搜索结果
        """
        return run_grep_search(self.config.repo_path, search_terms, self.config.is_regex)
    
    def _perform_validation(self, matched_results: List[Dict[str, Any]], search_terms: List[str] | str) -> List[Dict[str, Any]]:
        """
        执行二次校验
        
        Args:
            matched_results: 初步搜索结果
            search_terms: 搜索词列表或单个搜索词
            
        Returns:
            校验后的结果
        """
        logger.info(f"启用二次校验，使用 {self.config.validate_workers} 个工作进程")
        return parallel_validate(
            matched_results, 
            search_terms, 
            self.config.is_regex, 
            self.config.validate_workers
        )