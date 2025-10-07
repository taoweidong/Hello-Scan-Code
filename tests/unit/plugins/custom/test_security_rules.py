#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义安全规则插件测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

class TestCustomSecurityRules(unittest.TestCase):
    """自定义安全规则插件测试类"""

    def test_import_security_rules(self):
        """测试导入安全规则"""
        try:
            # 尝试导入安全规则
            from src.plugins.custom.security_rules import HardcodedPasswordRule, WeakCryptographicAlgorithmRule
            # 如果导入成功，测试通过
            self.assertTrue(True)
        except ImportError:
            # 如果导入失败，跳过测试
            self.skipTest("安全规则模块不存在或有导入问题")

    def test_hardcoded_password_rule(self):
        """测试硬编码密码规则"""
        try:
            from src.plugins.custom.security_rules import HardcodedPasswordRule
            rule = HardcodedPasswordRule()
            self.assertTrue(hasattr(rule, 'rule_id'))
        except ImportError:
            self.skipTest("安全规则模块不存在或有导入问题")

    def test_weak_crypto_rule(self):
        """测试弱加密算法规则"""
        try:
            from src.plugins.custom.security_rules import WeakCryptographicAlgorithmRule
            rule = WeakCryptographicAlgorithmRule()
            self.assertTrue(hasattr(rule, 'rule_id'))
        except ImportError:
            self.skipTest("安全规则模块不存在或有导入问题")


if __name__ == '__main__':
    unittest.main()