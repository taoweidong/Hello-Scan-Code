"""
内置关键字扫描插件
"""
from typing import List, Dict, Any
import re
from enum import Enum

# 定义严重级别枚举
class SeverityLevel(Enum):
    """问题严重级别"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class KeywordScanPlugin:
    """关键字扫描插件"""
    
    @property
    def plugin_id(self) -> str:
        return "builtin.keyword"
    
    @property
    def name(self) -> str:
        return "Keyword Scanner"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "基于关键字的代码扫描插件"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"
    
    def __init__(self):
        self.keywords = []
        self.case_sensitive = False
        self.initialized = False
    
    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php"]
    
    def get_grep_pattern(self) -> str:
        """构建grep搜索模式"""
        if not self.keywords:
            return ""
        
        # 将关键字转换为grep兼容的正则
        pattern = "|".join(re.escape(keyword) for keyword in self.keywords)
        return pattern
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.keywords = config.get("keywords", ["TODO", "FIXME", "BUG", "HACK"])
            self.case_sensitive = config.get("case_sensitive", False)
            self.initialized = True
            return True
        except Exception:
            return False
    
    def scan_line(self, file_path: str, line_number: int, line_content: str, 
                 context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """扫描单行内容"""
        if not self.initialized:
            return []
        
        results = []
        
        for keyword in self.keywords:
            if self.case_sensitive:
                found = keyword in line_content
            else:
                found = keyword.lower() in line_content.lower()
            
            if found:
                # 确定严重级别
                severity = self._get_severity_for_keyword(keyword)
                
                result = {
                    "plugin_id": self.plugin_id,
                    "file_path": file_path,
                    "line_number": line_number,
                    "message": f"发现关键字: {keyword}",
                    "severity": severity,
                    "rule_id": f"KEYWORD_{keyword}",
                    "category": "code_style",
                    "suggestion": "考虑处理或移除该标记",
                    "code_snippet": line_content.strip()
                }
                results.append(result)
        
        return results
    
    def _get_severity_for_keyword(self, keyword: str) -> str:
        """根据关键字确定严重级别"""
        severity_map = {
            "TODO": SeverityLevel.LOW.value,
            "FIXME": SeverityLevel.MEDIUM.value, 
            "HACK": SeverityLevel.MEDIUM.value,
            "BUG": SeverityLevel.HIGH.value,
            "XXX": SeverityLevel.MEDIUM.value,
        }
        return severity_map.get(keyword.upper(), SeverityLevel.LOW.value)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """返回配置schema"""
        return {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要搜索的关键字列表",
                    "default": ["TODO", "FIXME", "BUG", "HACK"]
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "是否区分大小写",
                    "default": False
                }
            }
        }