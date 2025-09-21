#!/usr/bin/env python3
"""
高效代码搜索工具主程序
"""

import os
import sys
from .logger_config import get_logger
from .config import parse_args, SearchConfig
from .code_searcher import CodeSearcher

logger = get_logger()


def main():
    """主函数"""
    try:
        # 解析配置，使用config文件中的默认值
        config = parse_args()
        
        # 允许在入口脚本中直接修改配置参数
        # 用户可以在这里直接修改配置，例如：
        # config.repo_path = "/path/to/your/repo"
        # config.search_term = "your_search_terms"
        # config.is_regex = True
        # config.validate = True
        # config.validate_workers = 8
        # config.db_path = "custom/path/results.db"
        # config.excel_path = "custom/path/results.xlsx"
        # config.log_level = "DEBUG"
        
        # 创建代码搜索器实例
        searcher = CodeSearcher(config)
        
        # 执行搜索
        matched_results = searcher.search()
        
        if not matched_results:
            logger.info("未找到匹配的文件")
            return
        
        # 保存结果
        searcher.save_results(matched_results)
        
        logger.info("搜索完成")
        
    except Exception as e:
        logger.error(f"搜索过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()