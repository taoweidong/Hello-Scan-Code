"""
JSON配置加载器

<<<<<<< HEAD
负责加载、验证和处理JSON格式的配置文件
=======
为新架构提供JSON配置文件支持
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
"""

import json
import os
import sys
<<<<<<< HEAD
from pathlib import Path
from typing import Dict, Any, Optional, Union
import jsonschema
from jsonschema import validate, ValidationError
from loguru import logger


class JSONConfigLoader:
    """JSON配置文件加载器"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            schema_path: JSON Schema文件路径，用于验证配置
        """
        self.schema_path = schema_path
        self._schema: Optional[Dict[str, Any]] = None
        self._default_config: Optional[Dict[str, Any]] = None
    
    def _get_executable_dir(self) -> Path:
        """获取可执行文件所在目录"""
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的环境
            return Path(sys.executable).parent
        else:
            # 开发环境
            return Path(__file__).parent.parent.parent
    
    def _load_schema(self) -> Dict[str, Any]:
        """加载JSON Schema"""
        if self._schema is not None:
            return self._schema
            
        if self.schema_path and os.path.exists(self.schema_path):
            schema_file = self.schema_path
        else:
            # 查找Schema文件
            exe_dir = self._get_executable_dir()
            possible_paths = [
                exe_dir / "config" / "config.schema.json",
                exe_dir / "config.schema.json",
                Path(__file__).parent.parent.parent / "config" / "config.schema.json"
            ]
            
            schema_file = None
            for path in possible_paths:
                if path.exists():
                    schema_file = str(path)
                    break
        
        if schema_file and os.path.exists(schema_file):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    self._schema = json.load(f)
                logger.debug(f"已加载配置Schema: {schema_file}")
            except Exception as e:
                logger.warning(f"加载配置Schema失败: {e}")
                self._schema = {}
        else:
            logger.warning("未找到配置Schema文件")
            self._schema = {}
            
        return self._schema or {}
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        if self._default_config is not None:
            return self._default_config
            
        exe_dir = self._get_executable_dir()
        possible_paths = [
            exe_dir / "config" / "default.json",
            exe_dir / "default.json",
            Path(__file__).parent.parent.parent / "config" / "default.json"
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self._default_config = json.load(f)
                    logger.debug(f"已加载默认配置: {path}")
                    return self._default_config
                except Exception as e:
                    logger.warning(f"加载默认配置失败 {path}: {e}")
                    continue
        
        # 硬编码的后备默认配置
        self._default_config = {
=======
from typing import Dict, Any, Optional, Type, TypeVar
from pathlib import Path
import logging

from .base_config import BaseConfig
from .app_config import AppConfig
from .logger_config import LoggerConfig
from .database_config import DatabaseConfig

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseConfig)


class JsonConfigLoader:
    """JSON配置加载器类"""
    
    CONFIG_FILENAME = "config.json"
    TEMPLATE_FILENAME = "config.template.json"
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化JSON配置加载器
        
        Args:
            config_dir: 配置文件目录，默认为可执行文件所在目录
        """
        self.config_dir = config_dir or self._get_executable_dir()
        self.config_path = os.path.join(self.config_dir, self.CONFIG_FILENAME)
        self.template_path = os.path.join(self.config_dir, self.TEMPLATE_FILENAME)
    
    @staticmethod
    def _get_executable_dir() -> str:
        """
        获取可执行文件所在目录
        
        Returns:
            str: 可执行文件目录路径
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的可执行文件
            return os.path.dirname(sys.executable)
        else:
            # 开发环境
            return os.getcwd()
    
    def load_json_config(self) -> Optional[Dict[str, Any]]:
        """
        加载JSON配置文件
        
        Returns:
            Optional[Dict[str, Any]]: 配置字典，如果加载失败返回None
        """
        if not os.path.exists(self.config_path):
            logger.info(f"JSON配置文件不存在: {self.config_path}")
            return None
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 基本验证
            if not isinstance(config_dict, dict):
                logger.error("JSON配置文件格式错误：根元素必须是对象")
                return None
            
            logger.info(f"成功加载JSON配置文件: {self.config_path}")
            return config_dict
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON配置文件格式错误: {e}")
            return None
        except Exception as e:
            logger.error(f"读取JSON配置文件失败: {e}")
            return None
    
    def apply_json_to_config(self, config: T, json_data: Dict[str, Any]) -> T:
        """
        将JSON配置应用到配置对象
        
        Args:
            config: 配置对象
            json_data: JSON配置数据
            
        Returns:
            T: 更新后的配置对象
        """
        config_type = type(config)
        
        if config_type == AppConfig:
            return self._apply_to_app_config(config, json_data)
        elif config_type == LoggerConfig:
            return self._apply_to_logger_config(config, json_data)
        elif config_type == DatabaseConfig:
            return self._apply_to_database_config(config, json_data)
        else:
            logger.warning(f"不支持的配置类型: {config_type}")
            return config
    
    def _apply_to_app_config(self, config: AppConfig, json_data: Dict[str, Any]) -> AppConfig:
        """应用JSON配置到AppConfig"""
        # 直接映射的字段
        direct_fields = [
            'repo_path', 'search_term', 'is_regex', 'validate', 'validate_workers'
        ]
        
        for field in direct_fields:
            if field in json_data:
                setattr(config, field, json_data[field])
        
        # 处理输出配置
        if 'output' in json_data:
            output_config = json_data['output']
            if 'db_path' in output_config:
                config.db_path = output_config['db_path']
            if 'excel_path' in output_config:
                config.excel_path = output_config['excel_path']
        
        # 处理过滤器配置
        if 'filters' in json_data:
            filters_config = json_data['filters']
            if 'ignore_dirs' in filters_config:
                config.ignore_dirs = filters_config['ignore_dirs']
            if 'file_extensions' in filters_config:
                config.file_extensions = filters_config['file_extensions']
        
        return config
    
    def _apply_to_logger_config(self, config: LoggerConfig, json_data: Dict[str, Any]) -> LoggerConfig:
        """应用JSON配置到LoggerConfig"""
        if 'logging' in json_data:
            logging_config = json_data['logging']
            if 'level' in logging_config:
                config.level = logging_config['level']
            if 'file_path' in logging_config:
                config.file_path = logging_config['file_path']
            if 'rotation' in logging_config:
                config.rotation = logging_config['rotation']
            if 'retention' in logging_config:
                config.retention = logging_config['retention']
        
        return config
    
    def _apply_to_database_config(self, config: DatabaseConfig, json_data: Dict[str, Any]) -> DatabaseConfig:
        """应用JSON配置到DatabaseConfig"""
        if 'database' in json_data:
            db_config = json_data['database']
            if 'url' in db_config:
                config.url = db_config['url']
            if 'pool_size' in db_config:
                config.pool_size = db_config['pool_size']
            if 'max_overflow' in db_config:
                config.max_overflow = db_config['max_overflow']
            if 'pool_timeout' in db_config:
                config.pool_timeout = db_config['pool_timeout']
        
        return config
    
    def save_config_template(self) -> None:
        """创建配置模板文件"""
        template_config = {
            "_comment": "Hello-Scan-Code 配置文件模板",
            "_description": "复制此文件为 config.json 并修改相应配置项",
            
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
            "repo_path": ".",
            "search_term": "test,def,void",
            "is_regex": False,
            "validate": False,
            "validate_workers": 4,
<<<<<<< HEAD
=======
            
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
            "output": {
                "db_path": "db/results.db",
                "excel_path": "report/results.xlsx"
            },
<<<<<<< HEAD
            "logging": {
                "level": "INFO"
            },
            "filters": {
                "ignore_dirs": [".git", "__pycache__", ".svn", ".hg", ".idea", ".vscode", "node_modules", ".tox"],
                "file_extensions": None
            }
        }
        logger.info("使用内置默认配置")
        return self._default_config
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，如果不指定则自动查找
            
        Returns:
            配置字典
        """
        # 加载默认配置作为基础
        config = self._load_default_config().copy()
        
        # 确定配置文件路径
        if config_path and os.path.exists(config_path):
            user_config_file = config_path
        else:
            # 自动查找配置文件
            exe_dir = self._get_executable_dir()
            possible_paths = [
                exe_dir / "config.json",
                Path.cwd() / "config.json",
                exe_dir / "config" / "config.json"
            ]
            
            user_config_file = None
            for path in possible_paths:
                if path.exists():
                    user_config_file = str(path)
                    break
        
        # 加载用户配置
        if user_config_file and os.path.exists(user_config_file):
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 递归合并配置
                config = self._merge_config(config, user_config)
                logger.info(f"已加载用户配置: {user_config_file}")
                
            except json.JSONDecodeError as e:
                logger.error(f"配置文件JSON格式错误 {user_config_file}: {e}")
                logger.warning("将使用默认配置")
            except Exception as e:
                logger.error(f"加载配置文件失败 {user_config_file}: {e}")
                logger.warning("将使用默认配置")
        else:
            logger.info("未找到用户配置文件，使用默认配置")
        
        # 验证配置
        if not self.validate_config(config):
            logger.warning("配置验证失败，使用默认配置")
            config = self._load_default_config().copy()
        
        return config
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归合并配置字典
        
        Args:
            base: 基础配置
            override: 覆盖配置
            
        Returns:
            合并后的配置
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否符合Schema
        
        Args:
            config: 配置字典
            
        Returns:
            验证是否通过
        """
        try:
            schema = self._load_schema()
            if schema:
                validate(instance=config, schema=schema)
            
            # 基本验证
            if not config.get('repo_path') or not config.get('search_term'):
                return False
                
            validate_workers = config.get('validate_workers', 4)
            if not isinstance(validate_workers, int) or validate_workers <= 0:
                return False
            
            return True
            
        except ValidationError as e:
            logger.error(f"配置验证失败: {e.message}")
            return False
        except Exception as e:
            logger.error(f"配置验证过程中发生错误: {e}")
            return False
    
    def save_template_config(self, output_path: str) -> bool:
        """
        保存配置模板文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            是否保存成功
        """
        try:
            exe_dir = self._get_executable_dir()
            template_paths = [
                exe_dir / "config" / "config.template.json",
                exe_dir / "config.template.json",
                Path(__file__).parent.parent.parent / "config" / "config.template.json"
            ]
            
            # 查找模板文件
            template_content = None
            for path in template_paths:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    break
            
            if not template_content:
                # 使用默认配置生成模板
                default_config = self._load_default_config()
                # 将repo_path设为"."用于模板
                default_config["repo_path"] = "."
                template_content = json.dumps(default_config, indent=2, ensure_ascii=False)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            logger.info(f"配置模板已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置模板失败: {e}")
            return False


# 全局配置加载器实例
_config_loader: Optional[JSONConfigLoader] = None


def get_config_loader() -> JSONConfigLoader:
    """获取全局配置加载器实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = JSONConfigLoader()
    return _config_loader


def load_json_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    便捷函数：加载JSON配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    return get_config_loader().load_config(config_path)
=======
            
            "logging": {
                "level": "INFO",
                "file_path": "logs/app.log",
                "rotation": "10 MB",
                "retention": "7 days"
            },
            
            "database": {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30
            },
            
            "filters": {
                "ignore_dirs": [
                    ".git", "__pycache__", ".svn", ".hg", ".idea",
                    ".vscode", "node_modules", ".tox", "dist", "build"
                ],
                "file_extensions": None
            }
        }
        
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.template_path, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置模板已创建: {self.template_path}")
        except Exception as e:
            logger.error(f"创建配置模板失败: {e}")
            raise
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置文件信息"""
        return {
            "config_dir": self.config_dir,
            "config_path": self.config_path,
            "template_path": self.template_path,
            "config_exists": os.path.exists(self.config_path),
            "template_exists": os.path.exists(self.template_path),
            "is_executable": getattr(sys, 'frozen', False)
        }


# 全局JSON配置加载器实例
_json_loader: Optional[JsonConfigLoader] = None


def get_json_loader() -> JsonConfigLoader:
    """获取全局JSON配置加载器实例"""
    global _json_loader
    if _json_loader is None:
        _json_loader = JsonConfigLoader()
    return _json_loader


def load_config_from_json(config: T) -> T:
    """
    从JSON配置文件加载配置
    
    Args:
        config: 配置对象
        
    Returns:
        T: 更新后的配置对象
    """
    loader = get_json_loader()
    json_data = loader.load_json_config()
    
    if json_data is not None:
        return loader.apply_json_to_config(config, json_data)
    
    return config


def create_config_template() -> None:
    """创建配置模板文件"""
    loader = get_json_loader()
    loader.save_config_template()
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
