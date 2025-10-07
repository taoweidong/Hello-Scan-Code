#!/usr/bin/env python3
"""
安全相关扫描规则
"""

from typing import List
from ...plugin import IScanRule, ScanResult
from ...plugins import register_plugin
import re


@register_plugin
class HardcodedPasswordRule(IScanRule):
    """硬编码密码检测规则"""
    
    @property
    def rule_id(self) -> str:
        return "SECURITY_001"
    
    @property
    def name(self) -> str:
        return "Hardcoded Password"
    
    @property
    def severity(self) -> str:
        return "ERROR"

    def supports_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".go", ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".yaml", ".yml"]

    def grep_pattern(self) -> str:
        # 筛选可能包含密码的赋值语句
        return r'(password|passwd|pwd|token|secret).*=.*["\'].*["\']'

    def analyze(self, file_path: str, line_no: int, line: str, context: dict) -> List[ScanResult]:
        # 进一步分析字符串内容是否为常见弱密码
        match = re.search(r'=\s*["\']([^"\']+)["\']', line, re.I)
        if match:
            value = match.group(1)
            if len(value) < 6 or value.lower() in ['123456', 'password', 'admin', 'root', 'guest']:
                return [ScanResult(
                    file_path=file_path,
                    line_number=line_no,
                    content=line.strip(),
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message="Hardcoded weak password detected"
                )]
        return []


@register_plugin
class WeakCryptographicAlgorithmRule(IScanRule):
    """弱加密算法检测规则"""
    
    @property
    def rule_id(self) -> str:
        return "SECURITY_002"
    
    @property
    def name(self) -> str:
        return "Weak Cryptographic Algorithm"
    
    @property
    def severity(self) -> str:
        return "WARN"

    def supports_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".go", ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".swift"]

    def grep_pattern(self) -> str:
        # 筛选可能使用弱加密算法的代码
        return r'(MD5|SHA1|DES|RC4)'

    def analyze(self, file_path: str, line_no: int, line: str, context: dict) -> List[ScanResult]:
        # 检查是否真的在使用弱加密算法
        weak_algorithms = ['MD5', 'SHA1', 'DES', 'RC4']
        for algorithm in weak_algorithms:
            if algorithm in line and not any(ignore in line for ignore in ['comment', 'note', 'todo']):
                return [ScanResult(
                    file_path=file_path,
                    line_number=line_no,
                    content=line.strip(),
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"Weak cryptographic algorithm {algorithm} detected"
                )]
        return []