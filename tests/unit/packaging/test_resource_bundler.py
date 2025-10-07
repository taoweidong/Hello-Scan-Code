#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源打包器测试
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.packaging.resource_bundler import ResourceBundler, bundle_resources, create_resource_manifest, validate_resources


class TestResourceBundler(unittest.TestCase):
    """资源打包器测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.bundler = ResourceBundler(self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_resource_bundler_init(self):
        """测试资源打包器初始化"""
        self.assertIsInstance(self.bundler, ResourceBundler)
        self.assertEqual(str(self.bundler.project_root), self.temp_dir)

    def test_collect_config_files(self):
        """测试收集配置文件"""
        # 创建测试配置目录和文件
        config_dir = Path(self.temp_dir) / "config"
        config_dir.mkdir()
        
        template_file = config_dir / "config.template.json"
        template_file.write_text('{"test": "config"}')
        
        config_file = config_dir / "app.json"
        config_file.write_text('{"app": "config"}')
        
        # 执行收集
        files = self.bundler.collect_config_files()
        
        # 验证结果
        self.assertIsInstance(files, list)

    def test_collect_database_files(self):
        """测试收集数据库文件"""
        # 创建测试数据库目录和文件
        db_dir = Path(self.temp_dir) / "src" / "database"
        migrations_dir = db_dir / "migrations"
        migrations_dir.mkdir(parents=True)
        
        migration_file = migrations_dir / "001_init.py"
        migration_file.write_text('# Migration file')
        
        # 执行收集
        files = self.bundler.collect_database_files()
        
        # 验证结果
        self.assertIsInstance(files, list)

    def test_collect_docs_files(self):
        """测试收集文档文件"""
        # 创建测试文档目录和文件
        docs_dir = Path(self.temp_dir) / "docs"
        docs_dir.mkdir()
        
        readme_file = docs_dir / "README.md"
        readme_file.write_text('# Test README')
        
        # 执行收集
        files = self.bundler.collect_docs_files()
        
        # 验证结果
        self.assertIsInstance(files, list)

    def test_collect_license_files(self):
        """测试收集许可证文件"""
        # 创建测试许可证文件
        license_file = Path(self.temp_dir) / "LICENSE"
        license_file.write_text('Test License')
        
        readme_file = Path(self.temp_dir) / "README.md"
        readme_file.write_text('# Test README')
        
        # 执行收集
        files = self.bundler.collect_license_files()
        
        # 验证结果
        self.assertIsInstance(files, list)

    def test_collect_all_resources(self):
        """测试收集所有资源文件"""
        # 创建一些测试文件
        config_dir = Path(self.temp_dir) / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"
        config_file.write_text('{"test": "config"}')
        
        # 执行收集
        files = self.bundler.collect_all_resources()
        
        # 验证结果
        self.assertIsInstance(files, list)

    @patch('src.packaging.resource_bundler.json.dump')
    def test_create_resource_manifest(self, mock_json_dump):
        """测试创建资源清单"""
        # 配置模拟对象
        mock_json_dump.return_value = None
        
        # 执行创建清单
        manifest_path = self.bundler.create_resource_manifest()
        
        # 验证结果
        self.assertIsInstance(manifest_path, str)

    def test_validate_resources(self):
        """测试验证资源文件"""
        # 创建一些测试文件
        config_dir = Path(self.temp_dir) / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"
        config_file.write_text('{"test": "config"}')
        
        # 执行验证
        result = self.bundler.validate_resources()
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("total_files", result)
        self.assertIn("existing_files", result)
        self.assertIn("missing_files", result)
        self.assertIn("is_valid", result)

    def test_copy_resources_to_dist(self):
        """测试复制资源到分发目录"""
        # 创建目标分发目录
        dist_dir = Path(self.temp_dir) / "dist"
        
        # 执行复制
        result = self.bundler.copy_resources_to_dist(str(dist_dir))
        
        # 验证结果
        self.assertIsInstance(result, bool)

    def test_bundle_resources_function(self):
        """测试打包资源便捷函数"""
        files = bundle_resources(self.temp_dir)
        self.assertIsInstance(files, list)

    def test_create_resource_manifest_function(self):
        """测试创建资源清单便捷函数"""
        with patch('src.packaging.resource_bundler.ResourceBundler.create_resource_manifest') as mock_create:
            mock_create.return_value = "test_manifest.json"
            manifest_path = create_resource_manifest(self.temp_dir)
            self.assertEqual(manifest_path, "test_manifest.json")

    def test_validate_resources_function(self):
        """测试验证资源便捷函数"""
        with patch('src.packaging.resource_bundler.ResourceBundler.validate_resources') as mock_validate:
            mock_validate.return_value = {"is_valid": True}
            result = validate_resources(self.temp_dir)
            self.assertEqual(result, {"is_valid": True})


if __name__ == '__main__':
    unittest.main()