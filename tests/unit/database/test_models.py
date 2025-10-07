#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.models import ScanResultModel, ScanSummaryModel


class TestDatabaseModels(unittest.TestCase):
    """数据库模型测试类"""

    def test_scan_result_creation(self):
        """测试扫描结果创建"""
        scan_result = ScanResultModel(
            plugin_id="keyword",
            file_path="test.py",
            line_number=10,
            message="发现待办事项",
            severity="medium",
            rule_id="TODO001",
            category="comment",
            code_snippet="TODO: 实现功能"
        )
        
        self.assertEqual(scan_result.plugin_id, "keyword")
        self.assertEqual(scan_result.file_path, "test.py")
        self.assertEqual(scan_result.line_number, 10)
        self.assertEqual(scan_result.message, "发现待办事项")
        self.assertEqual(scan_result.severity, "medium")
        self.assertEqual(scan_result.rule_id, "TODO001")
        self.assertEqual(scan_result.category, "comment")
        self.assertEqual(scan_result.code_snippet, "TODO: 实现功能")

    def test_scan_summary_creation(self):
        """测试扫描摘要创建"""
        scan_summary = ScanSummaryModel(
            total_files=100,
            total_results=50,
            scan_duration=10.5
        )
        
        self.assertEqual(scan_summary.total_files, 100)
        self.assertEqual(scan_summary.total_results, 50)
        self.assertEqual(scan_summary.scan_duration, 10.5)


if __name__ == '__main__':
    unittest.main()