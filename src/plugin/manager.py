"""
插件管理器 - 负责插件的加载、注册和生命周期管理
"""
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
            for plugin_dir in plugin_dirs:
                if Path(plugin_dir).exists():
                    self._load_external_plugins(plugin_dir)
            
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
            # 动态导入内置插件包
            from ..plugins import builtin
            builtin_path = Path(builtin.__file__).parent
            
            for module_info in pkgutil.iter_modules([str(builtin_path)]):
                if module_info.ispkg:
                    continue
                    
                module_name = f"src.plugins.builtin.{module_info.name}"
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
                    module = importlib.import_module(f"plugins.{package_name}")
                    self._register_plugins_from_module(module)
                    
                except Exception as e:
                    logger.error(f"加载插件包 {package_name} 失败: {e}")
    
    def _load_plugin_module(self, module_name: str):
        """加载插件模块"""
        try:
            module = importlib.import_module(module_name)
            self._register_plugins_from_module(module)
        except Exception as e:
            logger.error(f"加载插件模块 {module_name} 失败: {e}")
    
    def _register_plugins_from_module(self, module):
        """从模块中注册所有插件类"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, IScanPlugin) and 
                obj != IScanPlugin and 
                obj != IAdvancedScanPlugin):
                
                try:
                    plugin_instance = obj()
                    self.registry.register_plugin(plugin_instance)
                    logger.debug(f"注册插件: {plugin_instance.plugin_id}")
                except Exception as e:
                    logger.error(f"注册插件 {name} 失败: {e}")
    
    def _initialize_plugins(self):
        """初始化所有插件"""
        plugin_configs = self.config_manager.get_plugin_configs()
        
        for plugin in self.registry.get_all_plugins():
            plugin_id = plugin.plugin_id
            config = plugin_configs.get(plugin_id, {})
            
            try:
                if plugin.initialize(config):
                    self.plugins[plugin_id] = plugin
                    logger.info(f"插件 {plugin_id} 初始化成功")
                else:
                    logger.warning(f"插件 {plugin_id} 初始化失败")
            except Exception as e:
                logger.error(f"初始化插件 {plugin_id} 时出错: {e}")
    
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