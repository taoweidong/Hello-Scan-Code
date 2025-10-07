"""
配置管理器 - 负责加载和管理配置
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # 使用默认配置
                self.config = self._get_default_config()
                self._save_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "repo_path": ".",
            "ignore_dirs": [".git", "node_modules", "venv", "__pycache__", "build", "dist"],
            "file_extensions": [".py", ".js", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php", ".cs", ".ts"],
            "plugins": {
                "enabled": ["builtin.keyword", "builtin.security", "builtin.todo"],
                "dirs": ["src/plugins/custom/"]
            },
            "output": {
                "report_dir": "report/",
                "export_formats": ["excel", "html"]
            },
            "scan": {
                "timeout": 300,
                "max_file_size": 10485760  # 10MB
            }
        }
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def get_repo_path(self) -> str:
        """获取仓库路径"""
        return self.config.get("repo_path", ".")
    
    def get_ignore_dirs(self) -> List[str]:
        """获取忽略目录列表"""
        return self.config.get("ignore_dirs", [])
    
    def get_file_extensions(self) -> List[str]:
        """获取文件扩展名列表"""
        return self.config.get("file_extensions", [])
    
    def get_enabled_plugins(self) -> List[str]:
        """获取启用的插件列表"""
        return self.config.get("plugins", {}).get("enabled", [])
    
    def get_plugin_dirs(self) -> List[str]:
        """获取插件目录列表"""
        return self.config.get("plugins", {}).get("dirs", [])
    
    def get_report_dir(self) -> str:
        """获取报告目录"""
        return self.config.get("output", {}).get("report_dir", "report/")
    
    def get_export_formats(self) -> List[str]:
        """获取导出格式列表"""
        return self.config.get("output", {}).get("export_formats", ["excel"])
    
    def get_scan_timeout(self) -> int:
        """获取扫描超时时间"""
        return self.config.get("scan", {}).get("timeout", 300)
    
    def get_max_file_size(self) -> int:
        """获取最大文件大小"""
        return self.config.get("scan", {}).get("max_file_size", 10485760)
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """获取特定插件的配置"""
        return self.config.get("plugin_configs", {}).get(plugin_id, {})
    
    def get_plugin_configs(self) -> Dict[str, Any]:
        """获取所有插件的配置"""
        return self.config.get("plugin_configs", {})
    
    def set_config_value(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        current = self.config
        
        # 导航到最后一级
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # 设置值
        current[keys[-1]] = value
        self._save_config()
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        current = self.config
        
        # 导航到指定的键
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current