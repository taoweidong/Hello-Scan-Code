#!/usr/bin/env python3
"""
关键字搜索规则
"""

from typing import List
from ...plugin import IScanRule, ScanResult
from ...plugins import register_plugin


@register_plugin
class KeywordRule(IScanRule):
    """关键字搜索规则"""
    
    def __init__(self, search_terms=None):
        """
        初始化关键字规则
        
        Args:
            search_terms: 搜索词列表
        """
        self.search_terms = search_terms or []
    
    @property
    def rule_id(self) -> str:
        return "BUILTIN_KEYWORD"
    
    @property
    def name(self) -> str:
        return "Keyword Search"
    
    @property
    def severity(self) -> str:
        return "INFO"

    def supports_extensions(self) -> List[str]:
        # 支持所有文本文件
        return [".py", ".js", ".java", ".go", ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", 
                ".html", ".css", ".xml", ".json", ".yml", ".yaml", ".md", ".txt", ".sql", ".sh"]

    def grep_pattern(self) -> str:
        # 将搜索词转为正则表达式
        if not self.search_terms:
            return ""
        if len(self.search_terms) == 1:
            return self.search_terms[0]
        return "|".join(self.search_terms)  # 使用或操作符连接多个搜索词

    def analyze(self, file_path: str, line_no: int, line: str, context: dict) -> List[ScanResult]:
        # 检查行中是否包含搜索词
        for term in self.search_terms:
            if term in line:
                return [ScanResult(
                    file_path=file_path,
                    line_number=line_no,
                    content=line.strip(),
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"Found keyword: {term}"
                )]
        return []