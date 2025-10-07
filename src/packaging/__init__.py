"""
PyInstaller打包支持模块

提供PyInstaller钩子和资源打包功能，适配新的配置架构
"""

from .pyinstaller_hooks import (
    get_hidden_imports, 
    get_hook_dirs, 
    get_data_files,
    get_exclude_modules,
    get_collect_submodules,
    create_spec_options,
    get_analysis_options,
    get_exe_options
)
from .resource_bundler import (
    ResourceBundler, 
    bundle_resources, 
    create_resource_manifest,
    validate_resources
)

__all__ = [
    # PyInstaller钩子
    'get_hidden_imports',
    'get_hook_dirs', 
    'get_data_files',
    'get_exclude_modules',
    'get_collect_submodules',
    'create_spec_options',
    'get_analysis_options',
    'get_exe_options',
    
    # 资源打包器
    'ResourceBundler',
    'bundle_resources',
    'create_resource_manifest',
    'validate_resources'
]
