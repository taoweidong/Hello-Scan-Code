"""
插件系统基础接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import os

class SeverityLevel(Enum):
    """问题严重级别"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ScanResult:
    """扫描结果数据模型"""
    plugin_id: str
    file_path: str
    line_number: int
    column: int = 0
    message: str = ""
    severity: SeverityLevel = SeverityLevel.MEDIUM
    rule_id: str = ""
    category: str = ""
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class ScanContext:
    """扫描上下文信息"""
    repo_path: str
    file_encoding: str = "utf-8"
    config: Dict[str, Any] = None
    extra_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.extra_context is None:
            self.extra_context = {}

class IScanPlugin(ABC):
    """扫描插件基础接口"""
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """插件唯一标识"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件显示名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """插件作者"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """返回支持的文件扩展名列表"""
        pass
    
    @abstractmethod
    def get_grep_pattern(self) -> Optional[str]:
        """
        返回用于grep预扫描的正则表达式
        返回None表示跳过grep阶段（全量扫描）
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def scan_line(self, file_path: str, line_number: int, line_content: str, 
                 context: ScanContext) -> List[ScanResult]:
        """
        扫描单行内容（grep匹配后调用）
        """
        pass
    
    def scan_file(self, file_path: str, file_content: str, 
                 context: ScanContext) -> List[ScanResult]:
        """
        扫描整个文件（可选实现，用于不支持grep的插件）
        """
        return []
    
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """返回插件配置schema"""
        return {}

class IAdvancedScanPlugin(IScanPlugin):
    """高级扫描插件接口（支持项目级分析）"""
    
    @abstractmethod
    def scan_project(self, project_path: str, context: ScanContext) -> List[ScanResult]:
        """扫描整个项目"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """返回依赖的插件列表"""
        pass