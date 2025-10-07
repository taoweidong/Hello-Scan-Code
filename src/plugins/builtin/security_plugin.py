"""
安全检测插件
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

class SecurityScanPlugin:
    """安全敏感信息检测插件"""
    
    @property
    def plugin_id(self) -> str:
        return "builtin.security"
    
    @property
    def name(self) -> str:
        return "Security Scanner"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "检测代码中的安全敏感信息"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"
    
    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".go", ".yaml", ".yml", ".json"]
    
    def get_grep_pattern(self) -> str:
        return r"password|passwd|secret|token|key|pwd"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    def scan_line(self, file_path: str, line_number: int, line_content: str, 
                 context: Dict[str, Any]) -> List[Dict[str, Any]]:
        patterns = {
            r'password\s*=\s*["\'][^"\']*["\']': ("PASSWORD_LITERAL", "硬编码密码"),
            r'api[_-]?key\s*=\s*["\'][^"\']*["\']': ("API_KEY_LITERAL", "硬编码API密钥"),
            r'secret[_-]?token\s*=\s*["\'][^"\']*["\']': ("SECRET_TOKEN", "硬编码密钥")
        }
        
        results = []
        for pattern, (rule_id, desc) in patterns.items():
            if re.search(pattern, line_content, re.I):
                results.append({
                    "plugin_id": self.plugin_id,
                    "file_path": file_path,
                    "line_number": line_number,
                    "message": desc,
                    "severity": SeverityLevel.CRITICAL.value,
                    "rule_id": rule_id,
                    "category": "security",
                    "suggestion": "请使用环境变量或密钥管理服务",
                    "code_snippet": line_content.strip()
                })
        
        return results