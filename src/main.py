"""
Hello-Scan-Code 主程序入口
"""
import argparse
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from plugin.manager import PluginManager
from engine.scan_engine import OptimizedScanEngine
from exporters.excel_exporter import ExcelExporter
from exporters.html_exporter import HTMLExporter
from exporters.database_exporter import DatabaseExporter
from database.session_manager import DatabaseSessionManager
from database.repositories import ScanResultRepository, ScanSummaryRepository
from utils.platform_utils import is_windows

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Hello-Scan-Code - 高性能代码扫描工具')
    parser.add_argument(
        '-p', '--path',
        help='要扫描的代码仓库路径',
        default=None
    )
    parser.add_argument(
        '-c', '--config',
        help='配置文件路径',
        default='config.json'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='启用详细日志输出'
    )
    parser.add_argument(
        '--export-excel',
        help='导出Excel报告文件路径',
        default=None
    )
    parser.add_argument(
        '--export-html',
        help='导出HTML报告文件路径',
        default=None
    )
    parser.add_argument(
        '--export-db',
        action='store_true',
        help='导出结果到数据库'
    )
    
    return parser.parse_args()

def setup_logging(verbose: bool = False):
    """设置日志级别"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志
    setup_logging(args.verbose)
    
    try:
        # 加载配置
        config_manager = ConfigManager(args.config)
        logger.info("配置加载完成")
        
        # 初始化插件管理器
        plugin_manager = PluginManager(config_manager)
        if not plugin_manager.initialize():
            logger.error("插件管理器初始化失败")
            return 1
        logger.info("插件管理器初始化完成")
        
        # 创建扫描引擎
        scan_engine = OptimizedScanEngine(config_manager, plugin_manager)
        logger.info("扫描引擎创建完成")
        
        # 执行扫描
        logger.info("开始执行代码扫描...")
        results = scan_engine.scan(args.path)
        stats = scan_engine.get_stats()
        logger.info("代码扫描完成")
        
        # 输出统计信息
        logger.info(f"扫描统计: {stats}")
        
        # 导出结果
        export_results(results, stats, args, config_manager)
        
        logger.info("程序执行完成")
        return 0
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        return 1

def export_results(results: List[Dict[str, Any]], stats: Dict[str, Any], 
                  args: argparse.Namespace, config_manager: ConfigManager):
    """导出扫描结果"""
    try:
        # Excel导出
        if args.export_excel:
            excel_exporter = ExcelExporter(config_manager.get_report_dir())
            excel_file = excel_exporter.export(results, args.export_excel)
            logger.info(f"Excel报告已导出到: {excel_file}")
        
        # HTML导出
        if args.export_html:
            html_exporter = HTMLExporter(config_manager.get_report_dir())
            html_file = html_exporter.export(results, args.export_html)
            logger.info(f"HTML报告已导出到: {html_file}")
        
        # 数据库导出
        if args.export_db:
            db_session_manager = DatabaseSessionManager()
            result_repository = ScanResultRepository(db_session_manager)
            summary_repository = ScanSummaryRepository(db_session_manager)
            
            # 清除之前的结果
            db_exporter = DatabaseExporter(result_repository, summary_repository)
            db_exporter.clear_previous_results()
            
            # 导出结果
            saved_count = db_exporter.export(results)
            logger.info(f"已将 {saved_count} 条结果保存到数据库")
            
            # 导出摘要
            summary_data = {
                "total_files": stats.get("total_files", 0),
                "total_results": stats.get("results_count", 0),
                "scan_duration": stats.get("scan_time", 0),
                "started_at": None,  # 可以添加实际的开始时间
                "ended_at": None     # 可以添加实际的结束时间
            }
            db_exporter.export_summary(summary_data)
            
    except Exception as e:
        logger.error(f"导出结果时出错: {e}")

if __name__ == "__main__":
    sys.exit(main())