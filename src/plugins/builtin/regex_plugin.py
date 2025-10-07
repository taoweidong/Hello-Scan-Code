"""
正则表达式插件
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

class RegexScanPlugin:
    """正则表达式扫描插件"""
    
    @property
    def plugin_id(self) -> str:
        return "builtin.regex"
    
    @property
    def name(self) -> str:
        return "Regex Scanner"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "基于自定义正则表达式的代码扫描插件"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"
    
    def __init__(self):
        self.patterns = []
        self.initialized = False
    
    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php", ".cs", ".ts", ".sql", ".xml", ".html"]
    
    def get_grep_pattern(self) -> str:
        """构建grep搜索模式"""
        # 由于正则表达式可能很复杂，我们不在此处构建grep模式
        # 而是在插件处理时进行精确匹配
        return ""
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.patterns = config.get("patterns", [])
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
        
        for pattern_config in self.patterns:
            pattern = pattern_config.get("pattern", "")
            rule_id = pattern_config.get("rule_id", "REGEX_PATTERN")
            message = pattern_config.get("message", "匹配正则表达式")
            severity = pattern_config.get("severity", SeverityLevel.MEDIUM.value)
            category = pattern_config.get("category", "custom")
            suggestion = pattern_config.get("suggestion", "请检查代码")
            
            try:
                # 编译正则表达式
                regex = re.compile(pattern)
                if regex.search(line_content):
                    result = {
                        "plugin_id": self.plugin_id,
                        "file_path": file_path,
                        "line_number": line_number,
                        "message": message,
                        "severity": severity,
                        "rule_id": rule_id,
                        "category": category,
                        "suggestion": suggestion,
                        "code_snippet": line_content.strip()
                    }
                    results.append(result)
            except re.error as e:
                # 正则表达式语法错误
                result = {
                    "plugin_id": self.plugin_id,
                    "file_path": file_path,
                    "line_number": line_number,
                    "message": f"正则表达式语法错误: {str(e)}",
                    "severity": SeverityLevel.HIGH.value,
                    "rule_id": "REGEX_SYNTAX_ERROR",
                    "category": "configuration",
                    "suggestion": "请检查正则表达式语法",
                    "code_snippet": pattern
                }
                results.append(result)
        
        return results
    
    def get_config_schema(self) -> Dict[str, Any]:
        """返回配置schema"""
        return {
            "type": "object",
            "properties": {
                "patterns": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "rule_id": {"type": "string"},
                            "message": {"type": "string"},
                            "severity": {"type": "string"},
                            "category": {"type": "string"},
                            "suggestion": {"type": "string"}
                        },
                        "required": ["pattern"]
                    },
                    "description": "正则表达式模式列表"
                }
            }
        }