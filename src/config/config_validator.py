"""
配置验证器模块

提供JSON配置文件的格式验证和数据校验功能
"""

import os
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器类"""
    
    # JSON配置的模式定义
    CONFIG_SCHEMA = {
        "type": "object",
        "required": ["repo_path"],
        "properties": {
            "repo_path": {"type": "string"},
            "search_term": {"type": "string"},
            "is_regex": {"type": "boolean"},
            "validate": {"type": "boolean"},
            "validate_workers": {"type": "integer", "minimum": 1, "maximum": 32},
            "output": {
                "type": "object",
                "properties": {
                    "db_path": {"type": "string"},
                    "excel_path": {"type": "string"}
                }
            },
            "logging": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
                }
            },
            "filters": {
                "type": "object",
                "properties": {
                    "ignore_dirs": {"type": "array", "items": {"type": "string"}},
                    "file_extensions": {
                        "oneOf": [
                            {"type": "null"},
                            {"type": "array", "items": {"type": "string"}}
                        ]
                    }
                }
            }
        }
    }
    
    @staticmethod
    def validate_config(config_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证配置字典的格式和数据有效性
        
        Args:
            config_dict: 要验证的配置字典
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 基本类型检查
        if not isinstance(config_dict, dict):
            errors.append("配置必须是一个字典对象")
            return False, errors
        
        # 验证必需字段
        if "repo_path" not in config_dict:
            errors.append("缺少必需字段: repo_path")
        
        # 验证repo_path
        if "repo_path" in config_dict:
            repo_path = config_dict["repo_path"]
            if not isinstance(repo_path, str):
                errors.append("repo_path必须是字符串类型")
            elif not repo_path.strip():
                errors.append("repo_path不能为空")
        
        # 验证search_term
        if "search_term" in config_dict:
            search_term = config_dict["search_term"]
            if not isinstance(search_term, str):
                errors.append("search_term必须是字符串类型")
            elif not search_term.strip():
                errors.append("search_term不能为空")
        
        # 验证布尔类型字段
        for field in ["is_regex", "validate"]:
            if field in config_dict and not isinstance(config_dict[field], bool):
                errors.append(f"{field}必须是布尔类型")
        
        # 验证validate_workers
        if "validate_workers" in config_dict:
            workers = config_dict["validate_workers"]
            if not isinstance(workers, int):
                errors.append("validate_workers必须是整数类型")
            elif workers < 1 or workers > 32:
                errors.append("validate_workers必须在1-32之间")
        
        # 验证output配置
        if "output" in config_dict:
            output_config = config_dict["output"]
            if not isinstance(output_config, dict):
                errors.append("output配置必须是字典类型")
            else:
                for path_field in ["db_path", "excel_path"]:
                    if path_field in output_config:
                        path_value = output_config[path_field]
                        if not isinstance(path_value, str):
                            errors.append(f"output.{path_field}必须是字符串类型")
                        elif not path_value.strip():
                            errors.append(f"output.{path_field}不能为空")
        
        # 验证logging配置
        if "logging" in config_dict:
            logging_config = config_dict["logging"]
            if not isinstance(logging_config, dict):
                errors.append("logging配置必须是字典类型")
            else:
                if "level" in logging_config:
                    level = logging_config["level"]
                    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                    if not isinstance(level, str):
                        errors.append("logging.level必须是字符串类型")
                    elif level not in valid_levels:
                        errors.append(f"logging.level必须是以下值之一: {', '.join(valid_levels)}")
        
        # 验证filters配置
        if "filters" in config_dict:
            filters_config = config_dict["filters"]
            if not isinstance(filters_config, dict):
                errors.append("filters配置必须是字典类型")
            else:
                # 验证ignore_dirs
                if "ignore_dirs" in filters_config:
                    ignore_dirs = filters_config["ignore_dirs"]
                    if not isinstance(ignore_dirs, list):
                        errors.append("filters.ignore_dirs必须是数组类型")
                    else:
                        for i, dir_name in enumerate(ignore_dirs):
                            if not isinstance(dir_name, str):
                                errors.append(f"filters.ignore_dirs[{i}]必须是字符串类型")
                
                # 验证file_extensions
                if "file_extensions" in filters_config:
                    file_extensions = filters_config["file_extensions"]
                    if file_extensions is not None:
                        if not isinstance(file_extensions, list):
                            errors.append("filters.file_extensions必须是数组或null")
                        else:
                            for i, ext in enumerate(file_extensions):
                                if not isinstance(ext, str):
                                    errors.append(f"filters.file_extensions[{i}]必须是字符串类型")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_paths(config_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证配置中的路径有效性
        
        Args:
            config_dict: 配置字典
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证repo_path是否存在
        if "repo_path" in config_dict:
            repo_path = config_dict["repo_path"]
            if isinstance(repo_path, str) and repo_path.strip():
                # 处理相对路径
                if not os.path.isabs(repo_path):
                    repo_path = os.path.abspath(repo_path)
                
                if not os.path.exists(repo_path):
                    errors.append(f"仓库路径不存在: {repo_path}")
                elif not os.path.isdir(repo_path):
                    errors.append(f"仓库路径不是目录: {repo_path}")
        
        # 验证输出路径的父目录是否存在或可创建
        if "output" in config_dict and isinstance(config_dict["output"], dict):
            output_config = config_dict["output"]
            
            for path_field in ["db_path", "excel_path"]:
                if path_field in output_config:
                    path_value = output_config[path_field]
                    if isinstance(path_value, str) and path_value.strip():
                        parent_dir = os.path.dirname(path_value)
                        if parent_dir and not os.path.exists(parent_dir):
                            try:
                                os.makedirs(parent_dir, exist_ok=True)
                            except OSError as e:
                                errors.append(f"无法创建{path_field}的父目录 {parent_dir}: {e}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_full_config(cls, config_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        执行完整的配置验证
        
        Args:
            config_dict: 配置字典
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        all_errors = []
        
        # 格式验证
        format_valid, format_errors = cls.validate_config(config_dict)
        all_errors.extend(format_errors)
        
        # 如果格式验证通过，再进行路径验证
        if format_valid:
            path_valid, path_errors = cls.validate_paths(config_dict)
            all_errors.extend(path_errors)
        
        return len(all_errors) == 0, all_errors