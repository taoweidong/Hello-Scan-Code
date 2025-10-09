"""
优化扫描引擎 - 双阶段扫描架构
"""
import time
from typing import List, Dict, Any, Optional
from collections import defaultdict
import logging
from pathlib import Path

from .grep_scanner import GrepScanner
from src.plugin.manager import PluginManager
from src.plugin.base import IScanPlugin, ScanContext, ScanResult

logger = logging.getLogger(__name__)

class OptimizedScanEngine:
    """优化扫描引擎 - 采用grep预筛选 + 插件精准分析"""
    
    def __init__(self, config_manager, plugin_manager):
        self.config_manager = config_manager
        self.plugin_manager = plugin_manager
        logger.debug(f"扫描引擎初始化，插件管理器ID: {id(plugin_manager)}")
        self.grep_scanner: Optional[GrepScanner] = None
        self.stats = {
            'total_files': 0,
            'scanned_files': 0,
            'total_plugins': 0,
            'scan_time': 0,
            'results_count': 0
        }
    
    def scan(self, repo_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        执行代码扫描
        
        Args:
            repo_path: 代码仓库路径，为None时使用配置中的路径
            
        Returns:
            扫描结果列表
        """
        start_time = time.time()
        
        # 获取配置
        if repo_path is None:
            repo_path = self.config_manager.get_repo_path()
            
        # 确保repo_path是字符串
        if repo_path is None:
            repo_path = "."
        
        ignore_dirs = self.config_manager.get_ignore_dirs()
        file_extensions = self.config_manager.get_file_extensions()
        
        # 计算总文件数
        file_list = list(self._walk_files(repo_path, file_extensions))
        self.stats['total_files'] = len(file_list)
        logger.debug(f"总文件数: {self.stats['total_files']}")
        
        # 初始化扫描器
        self.grep_scanner = GrepScanner(str(repo_path), ignore_dirs)
        
        # 获取启用的插件
        enabled_plugins = self.plugin_manager.get_enabled_plugins()
        logger.debug(f"扫描引擎中获取到的插件数量: {len(enabled_plugins)}")
        logger.debug(f"扫描引擎中插件管理器ID: {id(self.plugin_manager)}")
        if enabled_plugins:
            logger.debug("扫描引擎中的插件:")
            for plugin in enabled_plugins:
                logger.debug(f"  - {plugin.plugin_id}: {plugin.name}")
        else:
            logger.debug("扫描引擎中没有获取到任何插件")
        
        self.stats['total_plugins'] = len(enabled_plugins)
        
        logger.info(f"开始扫描仓库: {repo_path}")
        logger.info(f"启用插件数量: {len(enabled_plugins)}")
        
        # 按grep模式分组插件
        pattern_groups = self._group_plugins_by_pattern(enabled_plugins)
        
        all_results = []
        
        # 第一阶段：grep预扫描 + 插件精准分析
        for pattern, plugins in pattern_groups.items():
            if pattern:  # 使用grep优化的插件
                logger.info(f"使用grep模式扫描: {pattern}")
                results = self._scan_with_grep(pattern, plugins, str(repo_path), file_extensions)
                all_results.extend(results)
        
        # 第二阶段：全量扫描插件（不支持grep的插件）
        fallback_plugins = [p for p in enabled_plugins if not p.get_grep_pattern()]
        if fallback_plugins:
            logger.info(f"执行全量扫描插件: {len(fallback_plugins)} 个")
            results = self._scan_fallback(fallback_plugins, str(repo_path), file_extensions)
            all_results.extend(results)
        
        # 更新统计信息
        self.stats['scan_time'] = int(time.time() - start_time)  # 转换为整数
        self.stats['results_count'] = len(all_results)
        
        logger.info(f"扫描完成，耗时: {self.stats['scan_time']:.2f}s")
        logger.info(f"发现问题: {self.stats['results_count']} 个")
        
        return all_results
    
    def _group_plugins_by_pattern(self, plugins) -> Dict[str, List]:
        """按grep模式分组插件"""
        groups = defaultdict(list)
        
        for plugin in plugins:
            pattern = plugin.get_grep_pattern()
            if pattern:
                # 合并相同的模式
                groups[pattern].append(plugin)
            else:
                # 无grep模式的插件单独分组
                groups[None].append(plugin)
        
        return dict(groups)
    
    def _scan_with_grep(self, pattern: str, plugins: List, 
                       repo_path: str, file_extensions: List[str]) -> List[Dict[str, Any]]:
        """使用grep预扫描进行优化扫描"""
        results = []
        
        try:
            # 执行grep扫描
            if self.grep_scanner is not None:
                grep_stream = self.grep_scanner.scan(pattern, file_extensions)
                
                # 创建扫描上下文
                context = ScanContext(repo_path=repo_path)
                
                # 处理grep结果
                match_count = 0
                for file_path, line_no, line_content in grep_stream:
                    match_count += 1
                    logger.debug(f"Grep匹配: {file_path}:{line_no}: {line_content}")
                    # 对每个匹配的行执行插件分析
                    for plugin in plugins:
                        # 检查文件类型支持
                        file_ext = Path(file_path).suffix
                        if hasattr(plugin, 'get_supported_extensions'):
                            supported_extensions = plugin.get_supported_extensions()
                            if file_ext not in supported_extensions:
                                continue
                        
                        # 执行插件扫描
                        if hasattr(plugin, 'scan_line'):
                            plugin_results = plugin.scan_line(
                                file_path, line_no, line_content, context
                            )
                            if plugin_results:
                                logger.debug(f"插件 {plugin.plugin_id} 发现问题: {len(plugin_results)} 个")
                            results.extend(plugin_results)
                
                logger.debug(f"Grep模式 '{pattern}' 找到 {match_count} 个匹配")
                    
        except Exception as e:
            logger.error(f"Grep扫描失败: {e}")
        
        return results
    
    def _scan_fallback(self, plugins: List, repo_path: str, 
                      file_extensions: List[str]) -> List[Dict[str, Any]]:
        """全量扫描回退方案"""
        results = []
        context = ScanContext(repo_path=repo_path)
        
        # 遍历所有文件
        for file_path in self._walk_files(repo_path, file_extensions):
            try:
                self.stats['scanned_files'] += 1
                file_ext = Path(file_path).suffix
                full_path = Path(repo_path) / file_path
                
                # 读取文件内容
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 对每个插件执行文件扫描
                for plugin in plugins:
                    if hasattr(plugin, 'get_supported_extensions'):
                        supported_extensions = plugin.get_supported_extensions()
                        if file_ext in supported_extensions:
                            if hasattr(plugin, 'scan_file'):
                                plugin_results = plugin.scan_file(
                                    file_path, content, context
                                )
                                results.extend(plugin_results)
                        
            except Exception as e:
                logger.debug(f"扫描文件 {file_path} 失败: {e}")
        
        return results
    
    def _walk_files(self, repo_path: str, file_extensions: List[str]):
        """遍历代码文件"""
        repo_path_obj = Path(repo_path)
        ignore_dirs = self.config_manager.get_ignore_dirs()  # 从配置中获取忽略目录
        
        for item in repo_path_obj.rglob('*'):
            if item.is_file():
                # 检查忽略目录
                if any(ignore in str(item) for ignore in ignore_dirs):
                    continue
                
                # 文件扩展名过滤
                if file_extensions and item.suffix not in file_extensions:
                    continue
                
                yield str(item.relative_to(repo_path_obj))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取扫描统计信息"""
        return self.stats.copy()