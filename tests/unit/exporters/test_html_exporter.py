#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML导出器测试
"""

import unittest
import sys
import os
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.exporters.html_exporter import HTMLExporter


class TestHTMLExporter(unittest.TestCase):
    """HTML导出器测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = HTMLExporter(self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_html_exporter_init(self):
        """测试HTML导出器初始化"""
        self.assertEqual(self.exporter.output_dir, self.temp_dir)

    def test_html_exporter_export(self):
        """测试HTML导出功能"""
        # 创建测试数据
        results = [
            {
                "plugin_id": "keyword",
                "file_path": "test.py",
                "line_number": 10,
                "message": "发现待办事项",
                "severity": "medium",
                "rule_id": "TODO001",
                "category": "comment",
                "suggestion": "处理待办事项",
                "code_snippet": "TODO: 实现功能"
            }
        ]
        
        # 执行导出
        output_file = self.exporter.export(results, "test_results.html")
        
        # 验证结果
        self.assertTrue(os.path.exists(output_file))
        # 检查文件内容是否包含预期的HTML标签
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<html", content)
            self.assertIn("代码扫描报告", content)
            self.assertIn("test.py", content)

    def test_html_exporter_export_summary(self):
        """测试HTML摘要导出功能"""
        # 创建测试数据
        summary = {
            "total_files": 100,
            "total_results": 50,
            "scan_duration": 10.5,
            "started_at": "2023-01-01 12:00:00",
            "ended_at": "2023-01-01 12:00:10"
        }
        
        # 执行导出
        output_file = self.exporter.export_summary(summary, "test_summary.html")
        
        # 验证结果
        self.assertTrue(os.path.exists(output_file))
        # 检查文件内容是否包含预期的HTML标签
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<html", content)
            self.assertIn("代码扫描摘要报告", content)
            self.assertIn("100", content)
            self.assertIn("50", content)


if __name__ == '__main__':
    unittest.main()