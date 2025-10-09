"""
Hello-Scan-Code 主程序入口
"""
import click
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


@click.command()
@click.option('-p', '--path', help='要扫描的代码仓库路径', default=None)
@click.option('-c', '--config', help='配置文件路径', default='config.json', show_default=True)
@click.option('-v', '--verbose', is_flag=True, help='启用详细日志输出')
@click.option('--export-excel', help='导出Excel报告文件路径', default=None)
@click.option('--export-html', help='导出HTML报告文件路径', default=None)
@click.option('--export-db', is_flag=True, help='导出结果到数据库')
def main(path, config, verbose, export_excel, export_html, export_db):
    """Hello-Scan-Code - 高性能代码扫描工具"""
    # 设置日志
    setup_logging(verbose)
    
    try:
        # 加载配置
        config_manager = ConfigManager(config)
        logger.info("配置加载完成")
        logger.debug(f"配置内容: {config_manager.config}")
        logger.debug(f"启用插件列表: {config_manager.get_enabled_plugins()}")
        logger.debug(f"插件目录列表: {config_manager.get_plugin_dirs()}")
        
        # 初始化插件管理器
        plugin_manager = PluginManager(config_manager)
        logger.debug(f"主程序中插件管理器ID: {id(plugin_manager)}")
        init_result = plugin_manager.initialize()
        logger.debug(f"插件管理器初始化结果: {init_result}")
        
        # 检查注册表中的插件
        registry_plugins = plugin_manager.registry.get_all_plugins()
        logger.debug(f"注册表中的插件数量: {len(registry_plugins)}")
        if registry_plugins:
            logger.debug("注册表中的插件:")
            for plugin in registry_plugins:
                logger.debug(f"  - {plugin.plugin_id}: {plugin.name}")
        
        # 检查启用的插件
        enabled_plugins = plugin_manager.get_enabled_plugins()
        logger.debug(f"启用的插件数量: {len(enabled_plugins)}")
        if enabled_plugins:
            logger.debug("启用的插件:")
            for plugin in enabled_plugins:
                logger.debug(f"  - {plugin.plugin_id}: {plugin.name}")
        
        if not init_result:
            logger.error("插件管理器初始化失败")
            return 1
            
        logger.info(f"插件管理器初始化完成，加载了 {len(enabled_plugins)} 个插件")
        
        # 显示加载的插件
        if enabled_plugins:
            logger.info("已加载的插件:")
            for plugin in enabled_plugins:
                logger.info(f"  - {plugin.plugin_id}: {plugin.name}")
        else:
            logger.warning("没有加载任何插件")
        
        # 创建扫描引擎
        scan_engine = OptimizedScanEngine(config_manager, plugin_manager)
        logger.info("扫描引擎创建完成")
        
        # 执行扫描
        logger.info("开始执行代码扫描...")
        results = scan_engine.scan(path)
        stats = scan_engine.get_stats()
        logger.info("代码扫描完成")
        
        # 输出统计信息
        logger.info(f"扫描统计: {stats}")
        
        # 导出结果
        # 创建一个类似argparse.Namespace的对象来保持兼容性
        class Args:
            def __init__(self, export_excel, export_html, export_db):
                self.export_excel = export_excel
                self.export_html = export_html
                self.export_db = export_db
        
        args = Args(export_excel, export_html, export_db)
        export_results(results, stats, args, config_manager)
        
        logger.info("程序执行完成")
        return 0
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        return 1


def export_results(results: List[Dict[str, Any]], stats: Dict[str, Any], 
                  args, config_manager: ConfigManager):
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


def setup_logging(verbose: bool = False):
    """设置日志级别"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    main()