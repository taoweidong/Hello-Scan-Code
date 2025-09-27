"""
资源打包器模块

提供资源文件的收集和打包功能，适配新的项目结构
"""

import os
import shutil
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ResourceBundler:
    """资源打包器类"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        初始化资源打包器
        
        Args:
            project_root: 项目根目录，默认为当前文件的项目根目录
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
    
    def collect_config_files(self) -> List[tuple]:
        """
        收集配置文件
        
        Returns:
            List[tuple]: [(源文件路径, 目标路径), ...]
        """
        data_files = []
        
        # 新架构的配置模板（如果存在config目录）
        config_dir = self.project_root / "config"
        if config_dir.exists():
            template_file = config_dir / "config.template.json"
            if template_file.exists():
                data_files.append((str(template_file), "config.template.json"))
            
            # 其他配置文件
            for config_file in config_dir.glob("*.json"):
                if config_file.name != "config.template.json":
                    data_files.append((str(config_file), f"config/{config_file.name}"))
        
        # 检查是否有在源码中的配置模板
        src_config_dir = self.project_root / "src" / "config"
        if src_config_dir.exists():
            template_dir = src_config_dir / "templates"
            if template_dir.exists():
                for template_file in template_dir.glob("*.json"):
                    data_files.append((str(template_file), f"templates/{template_file.name}"))
        
        return data_files
    
    def collect_database_files(self) -> List[tuple]:
        """
        收集数据库相关文件
        
        Returns:
            List[tuple]: [(源文件路径, 目标路径), ...]
        """
        data_files = []
        
        # 数据库迁移文件
        migrations_dir = self.project_root / "src" / "database" / "migrations"
        if migrations_dir.exists():
            for migration_file in migrations_dir.glob("*.py"):
                if migration_file.name != "__init__.py":
                    relative_path = f"database/migrations/{migration_file.name}"
                    data_files.append((str(migration_file), relative_path))
        
        # 数据库配置文件
        db_config_dir = self.project_root / "src" / "database" / "config"
        if db_config_dir.exists():
            for config_file in db_config_dir.glob("*.py"):
                if config_file.name != "__init__.py":
                    relative_path = f"database/config/{config_file.name}"
                    data_files.append((str(config_file), relative_path))
        
        return data_files
    
    def collect_template_files(self) -> List[tuple]:
        """
        收集模板文件
        
        Returns:
            List[tuple]: [(源文件路径, 目标路径), ...]
        """
        data_files = []
        
        # 搜索模板文件
        templates_dir = self.project_root / "templates"
        if templates_dir.exists():
            for template_file in templates_dir.rglob("*"):
                if template_file.is_file():
                    relative_path = template_file.relative_to(templates_dir)
                    target_path = f"templates/{relative_path}"
                    data_files.append((str(template_file), target_path))
        
        return data_files
    
    def collect_docs_files(self) -> List[tuple]:
        """
        收集文档文件
        
        Returns:
            List[tuple]: [(源文件路径, 目标路径), ...]
        """
        data_files = []
        
        # 文档目录
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*"):
                if doc_file.is_file() and doc_file.suffix in ['.md', '.txt', '.rst']:
                    relative_path = doc_file.relative_to(docs_dir)
                    target_path = f"docs/{relative_path}"
                    data_files.append((str(doc_file), target_path))
        
        return data_files
    
    def collect_license_files(self) -> List[tuple]:
        """
        收集许可证和主要文档文件
        
        Returns:
            List[tuple]: [(源文件路径, 目标路径), ...]
        """
        data_files = []
        
        # 许可证文件
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
        for license_file in license_files:
            license_path = self.project_root / license_file
            if license_path.exists():
                data_files.append((str(license_path), license_file))
                break
        
        # README文件
        readme_files = ["README.md", "README.txt", "README.rst"]
        for readme_file in readme_files:
            readme_path = self.project_root / readme_file
            if readme_path.exists():
                data_files.append((str(readme_path), readme_file))
                break
        
        # 其他重要文档
        important_docs = [
            "PYINSTALLER_GUIDE.md",
            "DATABASE_OPTIMIZATION_SUMMARY.md",
            "CHANGELOG.md"
        ]
        
        for doc_file in important_docs:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                data_files.append((str(doc_path), doc_file))
        
        return data_files
    
    def collect_all_resources(self) -> List[tuple]:
        """
        收集所有资源文件
        
        Returns:
            List[tuple]: [(源文件路径, 目标路径), ...]
        """
        all_data_files = []
        
        # 收集各类资源文件
        all_data_files.extend(self.collect_config_files())
        all_data_files.extend(self.collect_database_files())
        all_data_files.extend(self.collect_template_files())
        all_data_files.extend(self.collect_docs_files())
        all_data_files.extend(self.collect_license_files())
        
        # 去重
        unique_data_files = []
        seen = set()
        for source, target in all_data_files:
            if target not in seen:
                unique_data_files.append((source, target))
                seen.add(target)
        
        logger.info(f"收集到 {len(unique_data_files)} 个资源文件")
        return unique_data_files
    
    def create_resource_manifest(self, output_path: Optional[str] = None) -> str:
        """
        创建资源清单文件
        
        Args:
            output_path: 输出路径，默认为项目根目录下的resource_manifest.json
            
        Returns:
            str: 清单文件路径
        """
        if output_path is None:
            output_path = self.project_root / "resource_manifest.json"
        else:
            output_path = Path(output_path)
        
        resources = self.collect_all_resources()
        
        manifest = {
            "version": "1.0",
            "generated_by": "ResourceBundler",
            "total_files": len(resources),
            "resources": {
                "config_files": self.collect_config_files(),
                "database_files": self.collect_database_files(),
                "template_files": self.collect_template_files(),
                "docs_files": self.collect_docs_files(),
                "license_files": self.collect_license_files()
            },
            "all_files": resources
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        logger.info(f"资源清单已保存到: {output_path}")
        return str(output_path)
    
    def validate_resources(self) -> Dict[str, Any]:
        """
        验证资源文件的完整性
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        resources = self.collect_all_resources()
        missing_files = []
        existing_files = []
        
        for source, target in resources:
            if os.path.exists(source):
                existing_files.append((source, target))
            else:
                missing_files.append((source, target))
        
        result = {
            "total_files": len(resources),
            "existing_files": len(existing_files),
            "missing_files": len(missing_files),
            "missing_list": missing_files,
            "is_valid": len(missing_files) == 0
        }
        
        if missing_files:
            logger.warning(f"发现 {len(missing_files)} 个缺失的资源文件")
            for source, target in missing_files:
                logger.warning(f"  缺失: {source} -> {target}")
        else:
            logger.info("所有资源文件验证通过")
        
        return result
    
    def copy_resources_to_dist(self, dist_dir: str) -> bool:
        """
        将资源文件复制到分发目录
        
        Args:
            dist_dir: 分发目录路径
            
        Returns:
            bool: 是否成功
        """
        try:
            dist_path = Path(dist_dir)
            dist_path.mkdir(parents=True, exist_ok=True)
            
            resources = self.collect_all_resources()
            
            for source, target in resources:
                if os.path.exists(source):
                    target_path = dist_path / target
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target_path)
                    logger.debug(f"复制: {source} -> {target_path}")
            
            logger.info(f"成功复制 {len(resources)} 个资源文件到 {dist_dir}")
            return True
        
        except Exception as e:
            logger.error(f"复制资源文件失败: {e}")
            return False


def bundle_resources(project_root: Optional[str] = None) -> List[tuple]:
    """
    便捷函数：打包所有资源文件
    
    Args:
        project_root: 项目根目录
        
    Returns:
        List[tuple]: 资源文件列表
    """
    bundler = ResourceBundler(project_root)
    return bundler.collect_all_resources()


def create_resource_manifest(project_root: Optional[str] = None, 
                           output_path: Optional[str] = None) -> str:
    """
    便捷函数：创建资源清单
    
    Args:
        project_root: 项目根目录
        output_path: 输出路径
        
    Returns:
        str: 清单文件路径
    """
    bundler = ResourceBundler(project_root)
    return bundler.create_resource_manifest(output_path)


def validate_resources(project_root: Optional[str] = None) -> Dict[str, Any]:
    """
    便捷函数：验证资源文件
    
    Args:
        project_root: 项目根目录
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    bundler = ResourceBundler(project_root)
    return bundler.validate_resources()