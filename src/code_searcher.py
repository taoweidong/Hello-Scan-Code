#!/usr/bin/env python3
"""
高效代码搜索工具核心类
使用设计模式重构后的核心搜索器
"""

import os
import sys
from typing import List, Dict, Any
from .config import get_logger, AppConfig
from .search_template import DefaultSearchTemplate
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
        self.search_template = DefaultSearchTemplate(config)
        self.db_manager = DatabaseManager(config.db_path)
        # 为Excel导出器设置最大行数限制，避免Excel文件过大
        self.excel_exporter = ExcelExporter(config.excel_path, max_rows_per_file=100000)
        
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
        return self.search_template.search()
    
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