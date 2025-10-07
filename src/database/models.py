"""
数据库模型
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ScanResultModel:
    """扫描结果模型"""
    id: Optional[int] = None
    plugin_id: str = ""
    file_path: str = ""
    line_number: int = 0
    column: int = 0
    message: str = ""
    severity: str = "medium"
    rule_id: str = ""
    category: str = ""
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "plugin_id": self.plugin_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "message": self.message,
            "severity": self.severity,
            "rule_id": self.rule_id,
            "category": self.category,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(**data)

@dataclass
class ScanSummaryModel:
    """扫描摘要模型"""
    id: Optional[int] = None
    total_files: int = 0
    total_results: int = 0
    scan_duration: float = 0.0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "total_files": self.total_files,
            "total_results": self.total_results,
            "scan_duration": self.scan_duration,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(**data)