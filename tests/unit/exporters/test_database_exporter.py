#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库导出器测试
"""

import unittest
import sys
import os
from unittest.mock import Mock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.exporters.database_exporter import DatabaseExporter


class TestDatabaseExporter(unittest.TestCase):
    """数据库导出器测试类"""

    def setUp(self):
        """测试前准备"""
        self.mock_result_repository = Mock()
        self.mock_summary_repository = Mock()
        self.exporter = DatabaseExporter(self.mock_result_repository, self.mock_summary_repository)

    def test_database_exporter_init(self):
        """测试数据库导出器初始化"""
        self.assertIsInstance(self.exporter, DatabaseExporter)
        self.assertEqual(self.exporter.result_repository, self.mock_result_repository)
        self.assertEqual(self.exporter.summary_repository, self.mock_summary_repository)

    def test_database_exporter_export(self):
        """测试数据库导出功能"""
        # 配置模拟对象
        self.mock_result_repository.save_batch.return_value = 5
        
        # 创建测试数据
        results = [
            {
                "plugin_id": "keyword",
                "file_path": "test.py",
                "line_number": 10,
                "column": 0,
                "message": "发现待办事项",
                "severity": "medium",
                "rule_id": "TODO001",
                "category": "comment",
                "suggestion": "处理待办事项",
                "code_snippet": "TODO: 实现功能"
            }
        ]
        
        # 执行导出
        saved_count = self.exporter.export(results)
        
        # 验证结果
        self.assertEqual(saved_count, 5)
        self.mock_result_repository.save_batch.assert_called_once()

    def test_database_exporter_export_summary(self):
        """测试数据库摘要导出功能"""
        # 配置模拟对象
        self.mock_summary_repository.save.return_value = 1
        
        # 创建测试数据
        summary = {
            "total_files": 100,
            "total_results": 50,
            "scan_duration": 10.5,
            "started_at": "2023-01-01 12:00:00",
            "ended_at": "2023-01-01 12:00:10"
        }
        
        # 执行导出
        saved_count = self.exporter.export_summary(summary)
        
        # 验证结果
        self.assertEqual(saved_count, 1)
        self.mock_summary_repository.save.assert_called_once()

    def test_database_exporter_clear_previous_results(self):
        """测试清除之前的结果"""
        # 配置模拟对象
        self.mock_result_repository.delete_all.return_value = 10
        
        # 执行清除
        deleted_count = self.exporter.clear_previous_results()
        
        # 验证结果
        self.assertEqual(deleted_count, 10)
        self.mock_result_repository.delete_all.assert_called_once()


if __name__ == '__main__':
    unittest.main()