#!/usr/bin/env python3
"""
TODO无分配人检测规则
"""

from typing import List
from ...plugin import IScanRule, ScanResult
from ...plugins import register_plugin


@register_plugin
class TodoWithoutAssigneeRule(IScanRule):
    """TODO无分配人检测规则"""
    
    @property
    def rule_id(self) -> str:
        return "CUSTOM_001"
    
    @property
    def name(self) -> str:
        return "TODO without assignee"
    
    @property
    def severity(self) -> str:
        return "WARN"

    def supports_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".go", ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".swift"]

    def grep_pattern(self) -> str:
        # 快速筛选包含TODO的行
        return r'\bTODO\b'

    def analyze(self, file_path: str, line_no: int, line: str, context: dict) -> List[ScanResult]:
        # 精准判断：TODO后面没有@author/@assignee/@owner
        if "TODO" in line and not any(x in line for x in ["@author", "@assignee", "@owner"]):
            return [ScanResult(
                file_path=file_path,
                line_number=line_no,
                content=line.strip(),
                rule_id=self.rule_id,
                severity=self.severity,
                message="TODO comment missing assignee"
            )]
        return []