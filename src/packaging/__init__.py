"""
PyInstaller打包支持模块

<<<<<<< HEAD
提供PyInstaller打包相关的工具和配置支持
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
from loguru import logger


class PackagingHelper:
    """打包辅助工具"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        初始化打包辅助工具
        
        Args:
            project_root: 项目根目录路径
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent.parent.parent
        
        self.src_dir = self.project_root / "src"
        self.config_dir = self.project_root / "config"
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
    
    def prepare_build_environment(self) -> bool:
        """
        准备构建环境
        
        Returns:
            是否准备成功
        """
        try:
            # 创建必要的目录
            self.build_dir.mkdir(exist_ok=True)
            self.dist_dir.mkdir(exist_ok=True)
            
            # 创建平台特定的构建目录
            (self.build_dir / "windows").mkdir(exist_ok=True)
            (self.build_dir / "linux").mkdir(exist_ok=True)
            
            logger.info("构建环境准备完成")
            return True
            
        except Exception as e:
            logger.error(f"准备构建环境失败: {e}")
            return False
    
    def get_hidden_imports(self) -> List[str]:
        """
        获取需要隐式导入的模块列表
        
        Returns:
            隐式导入模块列表
        """
        return [
            'sqlalchemy.sql.default_comparator',
            'sqlalchemy.dialects.sqlite',
            'sqlalchemy.engine.strategies',
            'pandas._libs.writers',
            'pandas.io.formats.style',
            'openpyxl.compat',
            'openpyxl.writer.excel',
            'loguru._defaults',
            'loguru._colorama',
            'jsonschema.validators',
            'jsonschema._format',
        ]
    
    def get_data_files(self) -> List[tuple]:
        """
        获取需要打包的数据文件
        
        Returns:
            数据文件列表，格式为(source_path, dest_path)
        """
        data_files = []
        
        # 添加配置文件
        if self.config_dir.exists():
            for config_file in self.config_dir.glob("*.json"):
                data_files.append((str(config_file), "config/"))
        
        # 添加数据库迁移文件（如果存在）
        migrations_dir = self.src_dir / "database" / "migrations"
        if migrations_dir.exists():
            for migration_file in migrations_dir.rglob("*.py"):
                rel_path = migration_file.relative_to(self.src_dir)
                data_files.append((str(migration_file), str(rel_path.parent) + "/"))
        
        return data_files
    
    def create_spec_file(self, platform: str = "windows", onefile: bool = True) -> str:
        """
        创建PyInstaller spec文件
        
        Args:
            platform: 目标平台 ("windows" 或 "linux")
            onefile: 是否生成单文件
            
        Returns:
            spec文件路径
        """
        spec_content = self._get_spec_template(platform, onefile)
        
        spec_dir = self.build_dir / platform
        spec_file = spec_dir / "hello-scan-code.spec"
        
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        logger.info(f"已创建{platform}平台的spec文件: {spec_file}")
        return str(spec_file)
    
    def _get_spec_template(self, platform: str, onefile: bool) -> str:
        """
        获取spec文件模板
        
        Args:
            platform: 目标平台
            onefile: 是否生成单文件
            
        Returns:
            spec文件内容
        """
        hidden_imports = self.get_hidden_imports()
        data_files = self.get_data_files()
        
        # 构建隐式导入字符串
        hidden_imports_str = ",\n        ".join([f"'{imp}'" for imp in hidden_imports])
        
        # 构建数据文件字符串
        data_files_str = ",\n        ".join([f"(r'{src}', '{dst}')" for src, dst in data_files])
        
        # 平台特定配置
        exe_name = "hello-scan-code.exe" if platform == "windows" else "hello-scan-code"
        icon_path = "None"  # 可以后续添加图标支持
        
        spec_template = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{self.project_root / "main.py"}'],
    pathex=[r'{self.project_root}'],
    binaries=[],
    datas=[
        {data_files_str}
    ],
    hiddenimports=[
        {hidden_imports_str}
    ],
    hookspath=[r'{self.project_root / 'src' / 'packaging' / 'hooks'}'],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    {"a.binaries," if onefile else ""}
    {"a.zipfiles," if onefile else ""}
    {"a.datas," if onefile else ""}
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    {"upx_exclude=[]," if onefile else ""}
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_path}
)

{"" if onefile else '''
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hello-scan-code'
)
'''}
"""
        return spec_template
    
    def copy_resources_to_dist(self, dist_path: str) -> bool:
        """
        复制资源文件到分发目录
        
        Args:
            dist_path: 分发目录路径
            
        Returns:
            是否复制成功
        """
        try:
            dist_path_obj = Path(dist_path)
            
            # 复制配置模板
            if self.config_dir.exists():
                config_template = self.config_dir / "config.template.json"
                if config_template.exists():
                    shutil.copy2(str(config_template), str(dist_path_obj / "config.template.json"))
                    logger.info("已复制配置模板到分发目录")
            
            # 复制说明文件
            readme_path = self.project_root / "README.md"
            if readme_path.exists():
                shutil.copy2(str(readme_path), str(dist_path_obj / "README.md"))
                logger.info("已复制README到分发目录")
            
            return True
            
        except Exception as e:
            logger.error(f"复制资源文件失败: {e}")
            return False
    
    def create_package_info(self, dist_path: str, platform: str) -> bool:
        """
        创建打包信息文件
        
        Args:
            dist_path: 分发目录路径
            platform: 平台名称
            
        Returns:
            是否创建成功
        """
        try:
            package_info = {
                "name": "Hello-Scan-Code",
                "version": "1.0.0",
                "platform": platform,
                "build_date": "",
                "description": "高效代码搜索工具",
                "usage": {
                    "config": "复制config.template.json为config.json并修改配置",
                    "run": f"./hello-scan-code{'exe' if platform == 'windows' else ''}"
                }
            }
            
            # 添加构建时间
            from datetime import datetime
            package_info["build_date"] = datetime.now().isoformat()
            
            info_file = Path(dist_path) / "package-info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(package_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"已创建打包信息文件: {info_file}")
            return True
            
        except Exception as e:
            logger.error(f"创建打包信息文件失败: {e}")
            return False


def get_packaging_helper(project_root: Optional[str] = None) -> PackagingHelper:
    """
    获取打包辅助工具实例
    
    Args:
        project_root: 项目根目录
        
    Returns:
        PackagingHelper实例
    """
    return PackagingHelper(project_root)
=======
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
>>>>>>> 172855ff5c1efeb6adfd299ea559c10e6eccaf2a
