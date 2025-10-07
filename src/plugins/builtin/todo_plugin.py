"""
TODO检测插件
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

class TodoScanPlugin:
    """TODO检测插件"""
    
    @property
    def plugin_id(self) -> str:
        return "builtin.todo"
    
    @property
    def name(self) -> str:
        return "TODO Scanner"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "检测代码中的TODO注释"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"
    
    def __init__(self):
        self.initialized = False
    
    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php", ".cs", ".ts"]
    
    def get_grep_pattern(self) -> str:
        """构建grep搜索模式"""
        return r"TODO|FIXME|BUG|HACK|XXX"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        self.initialized = True
        return True
    
    def scan_line(self, file_path: str, line_number: int, line_content: str, 
                 context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """扫描单行内容"""
        if not self.initialized:
            return []
        
        results = []
        
        # 检查TODO相关关键字
        todo_patterns = [
            (r"TODO[:\s]*.*", "TODO", SeverityLevel.LOW.value),
            (r"FIXME[:\s]*.*", "FIXME", SeverityLevel.MEDIUM.value),
            (r"BUG[:\s]*.*", "BUG", SeverityLevel.HIGH.value),
            (r"HACK[:\s]*.*", "HACK", SeverityLevel.MEDIUM.value),
            (r"XXX[:\s]*.*", "XXX", SeverityLevel.MEDIUM.value),
        ]
        
        for pattern, keyword, severity in todo_patterns:
            if re.search(pattern, line_content, re.IGNORECASE):
                result = {
                    "plugin_id": self.plugin_id,
                    "file_path": file_path,
                    "line_number": line_number,
                    "message": f"发现{keyword}注释",
                    "severity": severity,
                    "rule_id": f"TODO_{keyword}",
                    "category": "code_style",
                    "suggestion": "考虑处理或移除该注释",
                    "code_snippet": line_content.strip()
                }
                results.append(result)
        
        return results
    
    def get_config_schema(self) -> Dict[str, Any]:
        """返回配置schema"""
        return {
            "type": "object",
            "properties": {
                "include_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要包含的TODO模式列表",
                    "default": ["TODO", "FIXME", "BUG", "HACK", "XXX"]
                }
            }
        }