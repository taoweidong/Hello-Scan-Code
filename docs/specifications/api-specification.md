# API规范文档

## 概述

本文档定义了Hello-Scan-Code系统的API接口规范，包括核心类接口、扩展接口和配置接口。

## 核心API接口

### 1. CodeSearcher 主控制器API

```python
class CodeSearcher:
    """代码搜索器主控制器"""
    
    def __init__(self, config: SearchConfig) -> None:
        """
        初始化搜索器
        
        Args:
            config: 搜索配置对象
        """
        pass
    
    def search(self) -> List[Dict[str, Any]]:
        """
        执行代码搜索
        
        Returns:
            搜索结果列表，每个结果包含：
            - file_path: 文件路径
            - line_number: 行号
            - matched_content: 匹配内容
            - search_terms: 搜索词
        """
        pass
    
    def save_results(self, results: List[Dict[str, Any]]) -> None:
        """
        保存搜索结果
        
        Args:
            results: 搜索结果列表
        """
        pass
```

### 2. SearchStrategy 策略接口

```python
from abc import ABC, abstractmethod

class SearchStrategy(ABC):
    """搜索策略抽象接口"""
    
    def __init__(self, config: SearchConfig) -> None:
        """
        初始化搜索策略
        
        Args:
            config: 搜索配置
        """
        self.config = config
    
    @abstractmethod
    def search(self, repo_path: str, search_terms: Union[List[str], str], 
               is_regex: bool = False) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            repo_path: 代码仓库路径
            search_terms: 搜索词
            is_regex: 是否为正则表达式
            
        Returns:
            搜索结果列表
        """
        pass
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """
        判断是否应该忽略文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否忽略
        """
        pass
```

## 配置API

### SearchConfig 配置类

```python
from dataclasses import dataclass, field
from typing import List, Union, Dict, Any

@dataclass
class SearchConfig:
    """搜索配置类"""
    
    # 基本配置
    repo_path: str
    search_terms: Union[List[str], str]
    
    # 文件过滤配置
    file_extensions: List[str] = field(default_factory=lambda: [])
    exclude_dirs: List[str] = field(default_factory=lambda: [
        '.git', '.svn', 'node_modules', '__pycache__'
    ])
    exclude_files: List[str] = field(default_factory=lambda: [])
    
    # 搜索配置
    is_regex: bool = False
    enable_second_check: bool = True
    search_strategy: str = "auto"  # auto, grep, python
    
    # 性能配置
    max_workers: int = 4
    
    # 输出配置
    db_path: str = "db/search_results.db"
    excel_path: str = "search_results.xlsx"
    max_excel_rows: int = 1000000
    
    # 日志配置
    log_level: str = "INFO"
    
    def validate(self) -> bool:
        """验证配置有效性"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchConfig':
        """从字典创建配置"""
        pass
```

## 扩展API

### 1. 自定义搜索策略

```python
class CustomSearchStrategy(SearchStrategy):
    """自定义搜索策略示例"""
    
    def search(self, repo_path: str, search_terms: Union[List[str], str], 
               is_regex: bool = False) -> List[Dict[str, Any]]:
        """实现自定义搜索逻辑"""
        results = []
        # 自定义搜索实现
        return results
```

### 2. 自定义验证器

```python
from abc import ABC, abstractmethod

class ValidationStrategy(ABC):
    """验证策略接口"""
    
    @abstractmethod
    def validate(self, result: Dict[str, Any], search_terms: Union[List[str], str]) -> bool:
        """验证单个搜索结果"""
        pass

class CustomValidator(ValidationStrategy):
    """自定义验证器示例"""
    
    def validate(self, result: Dict[str, Any], search_terms: Union[List[str], str]) -> bool:
        """实现自定义验证逻辑"""
        return True
```

## 返回值规范

### 搜索结果格式

```python
# 单个搜索结果格式
SearchResult = {
    "file_path": str,        # 文件路径
    "line_number": int,      # 行号 (从1开始)
    "matched_content": str,  # 匹配的行内容
    "search_terms": str      # 搜索词 (JSON字符串)
}

# 搜索结果列表
SearchResults = List[SearchResult]
```

### 错误处理

```python
# 异常类定义
class HelloScanCodeError(Exception):
    """基础异常类"""
    pass

class ConfigError(HelloScanCodeError):
    """配置错误"""
    pass

class SearchError(HelloScanCodeError):
    """搜索错误"""
    pass

class ValidationError(HelloScanCodeError):
    """验证错误"""
    pass
```

## 使用示例

### 基本使用

```python
from src.config import SearchConfig
from src.code_searcher import CodeSearcher

# 创建配置
config = SearchConfig(
    repo_path="/path/to/code",
    search_terms=["function", "class"],
    file_extensions=[".py", ".js"],
    is_regex=False
)

# 执行搜索
searcher = CodeSearcher(config)
results = searcher.search()
searcher.save_results(results)
```

### 高级使用

```python
# 使用正则表达式
config = SearchConfig(
    repo_path="/path/to/code",
    search_terms=r"def\s+\w+\s*\(",
    is_regex=True,
    search_strategy="python"
)

# 自定义配置
config = SearchConfig(
    repo_path="/path/to/code",
    search_terms=["TODO", "FIXME"],
    exclude_dirs=[".git", "node_modules", "dist"],
    max_workers=8,
    enable_second_check=False
)
```