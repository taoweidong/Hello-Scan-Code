#!/usr/bin/env python3
"""
高效代码搜索工具主程序
"""

import os
import sys
from .logger_config import get_logger
from .config import parse_args, SearchConfig
from .searcher import run_grep_search, parallel_validate
from .database import DatabaseManager
from .exporter import ExcelExporter

logger = get_logger()

def main():
    # 解析命令行参数，如果没有参数则使用默认配置
    config = parse_args()
    
    # 检查仓库路径是否存在
    if not os.path.exists(config.repo_path):
        logger.error(f"仓库路径不存在: {config.repo_path}")
        sys.exit(1)
    
    logger.info(f"开始搜索: {config.search_term}")
    logger.info(f"仓库路径: {config.repo_path}")
    logger.info(f"是否正则表达式: {config.is_regex}")
    
    # 使用grep进行初步搜索
    matched_results = run_grep_search(config.repo_path, config.search_term, config.is_regex)
    
    if not matched_results:
        logger.info("未找到匹配的文件")
        return
    
    total_matches = sum(len(item['matches']) for item in matched_results)
    logger.info(f"grep初步搜索找到 {len(matched_results)} 个文件，共 {total_matches} 个匹配行")
    
    # 如果启用二次校验
    if config.validate:
        logger.info(f"启用二次校验，使用 {config.validate_workers} 个工作进程")
        matched_results = parallel_validate(
            matched_results, 
            config.search_term, 
            config.is_regex, 
            config.validate_workers
        )
    
    if not matched_results:
        logger.info("二次校验后未找到匹配的文件")
        return
    
    total_matches = sum(len(item['matches']) for item in matched_results)
    logger.info(f"最终找到 {len(matched_results)} 个匹配文件，共 {total_matches} 个匹配行")
    
    # 保存到数据库
    db_manager = DatabaseManager(config.db_path)
    db_manager.save_results(matched_results)
    
    # 导出到Excel
    exporter = ExcelExporter(config.excel_path)
    exporter.export_to_excel(matched_results)
    
    logger.info("搜索完成")

if __name__ == "__main__":
    main()