"""
插件注册表 - 管理插件的注册和查找
"""
from typing import Dict, List, Optional
from .base import IScanPlugin
import logging

logger = logging.getLogger(__name__)

class PluginRegistry:
    """插件注册表"""
    
    def __init__(self):
        self._plugins: Dict[str, IScanPlugin] = {}
        self._plugins_by_category: Dict[str, List[IScanPlugin]] = {}
    
    def register_plugin(self, plugin: IScanPlugin) -> bool:
        """注册插件"""
        try:
            plugin_id = plugin.plugin_id
            if plugin_id in self._plugins:
                logger.warning(f"插件 {plugin_id} 已存在，将被覆盖")
            
            self._plugins[plugin_id] = plugin
            logger.debug(f"插件 {plugin_id} 注册成功")
            return True
        except Exception as e:
            logger.error(f"注册插件失败: {e}")
            return False
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """注销插件"""
        if plugin_id in self._plugins:
            del self._plugins[plugin_id]
            # 也从分类中移除
            for category_plugins in self._plugins_by_category.values():
                category_plugins[:] = [p for p in category_plugins if p.plugin_id != plugin_id]
            return True
        return False
    
    def get_plugin(self, plugin_id: str) -> Optional[IScanPlugin]:
        """根据ID获取插件"""
        return self._plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[IScanPlugin]:
        """获取所有插件"""
        return list(self._plugins.values())
    
    def get_plugins_by_category(self, category: str) -> List[IScanPlugin]:
        """根据分类获取插件"""
        return self._plugins_by_category.get(category, [])
    
    def add_plugin_to_category(self, plugin: IScanPlugin, category: str):
        """将插件添加到指定分类"""
        if category not in self._plugins_by_category:
            self._plugins_by_category[category] = []
        
        if plugin not in self._plugins_by_category[category]:
            self._plugins_by_category[category].append(plugin)
    
    def plugin_exists(self, plugin_id: str) -> bool:
        """检查插件是否存在"""
        return plugin_id in self._plugins