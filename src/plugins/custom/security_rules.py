#!/usr/bin/env python3
"""
安全相关扫描规则
"""

from typing import List, Dict, Any
from src.plugin.base import IScanPlugin, ScanContext, ScanResult, SeverityLevel
import re


class HardcodedPasswordRule(IScanPlugin):
    """硬编码密码检测规则"""
    
    @property
    def plugin_id(self) -> str:
        return "security.hardcoded_password"
    
    @property
    def name(self) -> str:
        return "Hardcoded Password"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "检测代码中的硬编码密码"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"

    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".go", ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".yaml", ".yml"]

    def get_grep_pattern(self) -> str:
        # 使用更简单的grep模式，只匹配password关键字
        return r"password"

    def initialize(self, config: Dict[str, Any]) -> bool:
        return True

    def scan_line(self, file_path: str, line_number: int, line_content: str, context: ScanContext) -> List[ScanResult]:
        # 进一步分析字符串内容是否为常见弱密码
        # 检查是否包含密码赋值语句
        if re.search(r'(password|passwd|pwd|token|secret)\s*=\s*["\'][^"\']*["\']', line_content, re.I):
            match = re.search(r'=\s*["\']([^"\']+)["\']', line_content, re.I)
            if match:
                value = match.group(1)
                if len(value) < 6 or value.lower() in ['123456', 'password', 'admin', 'root', 'guest']:
                    return [ScanResult(
                        plugin_id=self.plugin_id,
                        file_path=file_path,
                        line_number=line_number,
                        code_snippet=line_content.strip(),
                        rule_id="SECURITY_001",
                        severity=SeverityLevel.CRITICAL,
                        message="Hardcoded weak password detected",
                        category="security"
                    )]
        return []


class WeakCryptographicAlgorithmRule(IScanPlugin):
    """弱加密算法检测规则"""
    
    @property
    def plugin_id(self) -> str:
        return "security.weak_crypto"
    
    @property
    def name(self) -> str:
        return "Weak Cryptographic Algorithm"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "检测代码中的弱加密算法"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"

    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".go", ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".swift"]

    def get_grep_pattern(self) -> str:
        # 使用更简单的grep模式
        return r"MD5|SHA1|DES|RC4"

    def initialize(self, config: Dict[str, Any]) -> bool:
        return True

    def scan_line(self, file_path: str, line_number: int, line_content: str, context: ScanContext) -> List[ScanResult]:
        # 检查是否真的在使用弱加密算法
        weak_algorithms = ['MD5', 'SHA1', 'DES', 'RC4']
        results = []
        for algorithm in weak_algorithms:
            if algorithm in line_content and not any(ignore in line_content for ignore in ['comment', 'note', 'todo']):
                results.append(ScanResult(
                    plugin_id=self.plugin_id,
                    file_path=file_path,
                    line_number=line_number,
                    code_snippet=line_content.strip(),
                    rule_id="SECURITY_002",
                    severity=SeverityLevel.HIGH,
                    message=f"Weak cryptographic algorithm {algorithm} detected",
                    category="security"
                ))
        return results