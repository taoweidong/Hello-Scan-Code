#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库仓储模块测试
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.repositories import ScanResultRepository, ScanSummaryRepository


class TestDatabaseRepositories(unittest.TestCase):
    """数据库仓储模块测试类"""

    def setUp(self):
        """测试前准备"""
        self.mock_session_manager = Mock()

    def test_scan_result_repository_init(self):
        """测试扫描结果仓储初始化"""
        # 配置模拟对象，使其在创建表时不抛出异常
        self.mock_session_manager.execute_non_query.return_value = 0
        
        repository = ScanResultRepository(self.mock_session_manager)
        self.assertIsInstance(repository, ScanResultRepository)
        self.assertEqual(repository.session_manager, self.mock_session_manager)

    def test_scan_summary_repository_init(self):
        """测试扫描摘要仓储初始化"""
        # 配置模拟对象，使其在创建表时不抛出异常
        self.mock_session_manager.execute_non_query.return_value = 0
        
        repository = ScanSummaryRepository(self.mock_session_manager)
        self.assertIsInstance(repository, ScanSummaryRepository)
        self.assertEqual(repository.session_manager, self.mock_session_manager)

    @patch('src.database.repositories.ScanResultModel')
    def test_scan_result_repository_save(self, mock_model):
        """测试保存扫描结果"""
        # 配置模拟对象，使其在创建表时不抛出异常
        self.mock_session_manager.execute_non_query.side_effect = [0, 1]  # 第一次是创建表，第二次是插入数据
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        # 创建仓储实例
        repository = ScanResultRepository(self.mock_session_manager)
        
        # 创建测试数据
        mock_result = Mock()
        mock_result.plugin_id = "test.plugin"
        mock_result.file_path = "test.py"
        mock_result.line_number = 10
        mock_result.column = 0
        mock_result.message = "Test message"
        mock_result.severity = "medium"
        mock_result.rule_id = "TEST001"
        mock_result.category = "test"
        mock_result.suggestion = "Test suggestion"
        mock_result.code_snippet = "Test code"
        
        # 执行保存
        result = repository.save(mock_result)
        
        # 验证结果
        self.assertEqual(result, 1)
        # 验证execute_non_query被调用了两次（创建表 + 插入数据）
        self.assertEqual(self.mock_session_manager.execute_non_query.call_count, 2)

    def test_scan_result_repository_delete_all(self):
        """测试删除所有扫描结果"""
        # 配置模拟对象，使其在创建表时不抛出异常
        self.mock_session_manager.execute_non_query.side_effect = [0, 5]  # 第一次是创建表，第二次是删除数据
        
        # 创建仓储实例
        repository = ScanResultRepository(self.mock_session_manager)
        
        # 执行删除
        result = repository.delete_all()
        
        # 验证结果
        self.assertEqual(result, 5)
        # 验证execute_non_query被调用了两次（创建表 + 删除数据）
        self.assertEqual(self.mock_session_manager.execute_non_query.call_count, 2)

    def test_scan_summary_repository_save(self):
        """测试保存扫描摘要"""
        # 配置模拟对象，使其在创建表时不抛出异常
        self.mock_session_manager.execute_non_query.side_effect = [0, 1]  # 第一次是创建表，第二次是插入数据
        
        # 创建仓储实例
        repository = ScanSummaryRepository(self.mock_session_manager)
        
        # 创建测试数据
        mock_summary = Mock()
        mock_summary.total_files = 100
        mock_summary.total_results = 50
        mock_summary.scan_duration = 10.5
        mock_summary.started_at = "2023-01-01 12:00:00"
        mock_summary.ended_at = "2023-01-01 12:00:10"
        
        # 执行保存
        result = repository.save(mock_summary)
        
        # 验证结果
        self.assertEqual(result, 1)
        # 验证execute_non_query被调用了两次（创建表 + 插入数据）
        self.assertEqual(self.mock_session_manager.execute_non_query.call_count, 2)


if __name__ == '__main__':
    unittest.main()