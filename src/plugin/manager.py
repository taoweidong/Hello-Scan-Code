import importlib
import importlib.util  # 添加这行来修复importlib.util的导入问题
import inspect
import pkgutil
from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import logging
from .base import IScanPlugin, IAdvancedScanPlugin
from .registry import PluginRegistry
from .discovery import PluginDiscovery

logger = logging.getLogger(__name__)

class PluginManager:
    """插件管理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.registry = PluginRegistry()
        self.discovery = PluginDiscovery()
        self.plugins: Dict[str, IScanPlugin] = {}
        self._initialized = False
        
    def initialize(self) -> bool:
        """初始化插件管理器"""
        if self._initialized:
            return True
            
        try:
            # 加载内置插件
            self._load_builtin_plugins()
            
            # 加载外部插件
            plugin_dirs = self.config_manager.get_plugin_dirs()
            logger.debug(f"Plugin dirs from config: {plugin_dirs}")
            for plugin_dir in plugin_dirs:
                if Path(plugin_dir).exists():
                    logger.debug(f"Loading external plugins from: {plugin_dir}")
                    self._load_external_plugins(plugin_dir)
                else:
                    logger.warning(f"Plugin directory does not exist: {plugin_dir}")
            
            # 初始化所有插件
            self._initialize_plugins()
            
            self._initialized = True
            logger.info(f"插件管理器初始化完成，加载了 {len(self.plugins)} 个插件")
            return True
            
        except Exception as e:
            logger.error(f"插件管理器初始化失败: {e}")
            return False
    
    def _load_builtin_plugins(self):
        """加载内置插件"""
        try:
            # 直接导入内置插件模块
            builtin_plugins = [
                'src.plugins.builtin.keyword_plugin',
                'src.plugins.builtin.regex_plugin',
                'src.plugins.builtin.security_plugin',
                'src.plugins.builtin.todo_plugin'
            ]
            
            for module_name in builtin_plugins:
                self._load_plugin_module(module_name)
                
        except Exception as e:
            logger.error(f"加载内置插件失败: {e}")
    
    def _load_external_plugins(self, plugin_dir: str):
        """加载外部插件"""
        plugin_path = Path(plugin_dir)
        
        for item in plugin_path.iterdir():
            if item.is_file() and item.suffix == '.py' and item.name != '__init__.py':
                # 直接导入Python文件
                try:
                    logger.debug(f"Loading plugin file: {item}")
                    spec = importlib.util.spec_from_file_location(item.stem, item)
                    if spec is not None:  # 添加空值检查
                        module = importlib.util.module_from_spec(spec)
                        if spec.loader is not None:  # 添加空值检查
                            spec.loader.exec_module(module)
                        self._register_plugins_from_module(module)
                    
                except Exception as e:
                    logger.error(f"加载插件文件 {item} 失败: {e}")
                    
            elif item.is_dir() and (item / '__init__.py').exists():
                # 导入插件包
                package_name = item.name
                try:
                    logger.debug(f"Loading plugin package: {package_name}")
                    module = importlib.import_module(f"plugins.{package_name}")
                    self._register_plugins_from_module(module)
                    
                except Exception as e:
                    logger.error(f"加载插件包 {package_name} 失败: {e}")
    
    def _load_plugin_module(self, module_name: str):
        """加载插件模块"""
        try:
            logger.debug(f"Loading plugin module: {module_name}")
            module = importlib.import_module(module_name)
            self._register_plugins_from_module(module)
        except Exception as e:
            logger.error(f"加载插件模块 {module_name} 失败: {e}")
    
    def _register_plugins_from_module(self, module):
        """从模块中注册所有插件类"""
        logger.debug(f"Registering plugins from module: {module.__name__}")
        members = inspect.getmembers(module)
        logger.debug(f"Module members: {[name for name, obj in members]}")
        for name, obj in members:
            logger.debug(f"Checking member: {name}, isclass: {inspect.isclass(obj)}")
            if inspect.isclass(obj):
                # 检查类是否继承自IScanPlugin
                is_scan_plugin = False
                try:
                    # 使用字符串比较来避免模块导入问题
                    if hasattr(obj, '__bases__'):
                        for base in obj.__bases__:
                            if 'IScanPlugin' in str(base):
                                is_scan_plugin = True
                                break
                except Exception as e:
                    logger.debug(f"Error checking base classes: {e}")
                
                logger.debug(f"Class {name} is scan plugin: {is_scan_plugin}")
            
            # 简化的检查逻辑
            if (inspect.isclass(obj) and 
                hasattr(obj, '__bases__') and
                any('IScanPlugin' in str(base) for base in obj.__bases__) and
                'IScanPlugin' not in name and 
                'IAdvancedScanPlugin' not in name):
                
                try:
                    plugin_instance = obj()
                    result = self.registry.register_plugin(plugin_instance)
                    logger.debug(f"注册插件结果: {result}")
                    logger.debug(f"注册插件: {plugin_instance.plugin_id}")
                except Exception as e:
                    logger.error(f"注册插件 {name} 失败: {e}")
            else:
                logger.debug(f"Skipping member {name}")
    
    def _initialize_plugins(self):
        """初始化所有插件"""
        plugin_configs = self.config_manager.get_plugin_configs()
        enabled_plugins = self.config_manager.get_enabled_plugins()
        logger.debug(f"Enabled plugins from config: {enabled_plugins}")
        
        # 检查注册表中的插件
        all_plugins = self.registry.get_all_plugins()
        logger.debug(f"注册表中的插件数量: {len(all_plugins)}")
        if all_plugins:
            logger.debug("注册表中的插件:")
            for plugin in all_plugins:
                logger.debug(f"  - {plugin.plugin_id}: {plugin.name}")
        else:
            logger.debug("注册表中没有插件")
        
        for plugin in all_plugins:
            plugin_id = plugin.plugin_id
            config = plugin_configs.get(plugin_id, {})
            
            # 只初始化启用的插件
            if plugin_id in enabled_plugins:
                try:
                    if plugin.initialize(config):
                        self.plugins[plugin_id] = plugin
                        logger.info(f"插件 {plugin_id} 初始化成功")
                    else:
                        logger.warning(f"插件 {plugin_id} 初始化失败")
                except Exception as e:
                    logger.error(f"初始化插件 {plugin_id} 时出错: {e}")
            else:
                logger.debug(f"插件 {plugin_id} 未启用，跳过初始化")
    
    def get_enabled_plugins(self) -> List[IScanPlugin]:
        """获取所有启用的插件"""
        return list(self.plugins.values())
    
    def get_plugin(self, plugin_id: str) -> Optional[IScanPlugin]:
        """根据ID获取插件"""
        return self.plugins.get(plugin_id)
    
    def get_plugins_by_extension(self, extension: str) -> List[IScanPlugin]:
        """获取支持指定文件扩展名的插件"""
        return [
            plugin for plugin in self.plugins.values()
            if extension in plugin.get_supported_extensions()
        ]
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """重新加载插件"""
        # 实现插件热重载逻辑
        return False  # 添加返回值来修复类型错误
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            plugin.cleanup()
            del self.plugins[plugin_id]
            return True
        return False