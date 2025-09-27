# 数据模型规范

## 概述

本文档定义了Hello-Scan-Code系统的数据模型，包括数据库模式、配置模型和业务对象模型。

## 数据库模型

### 1. SQLite 数据库模式

```sql
-- 搜索结果表
CREATE TABLE IF NOT EXISTS search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    matched_content TEXT NOT NULL,
    search_terms TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_path, line_number, search_terms)
);

-- 索引定义
CREATE INDEX IF NOT EXISTS idx_file_path ON search_results(file_path);
CREATE INDEX IF NOT EXISTS idx_search_terms ON search_results(search_terms);
CREATE INDEX IF NOT EXISTS idx_created_at ON search_results(created_at);
CREATE INDEX IF NOT EXISTS idx_composite ON search_results(file_path, line_number);
```

### 2. 数据字段说明

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 自增主键 |
| file_path | TEXT | NOT NULL | 文件路径（相对路径） |
| line_number | INTEGER | NOT NULL | 行号（从1开始） |
| matched_content | TEXT | NOT NULL | 匹配的行内容 |
| search_terms | TEXT | NOT NULL | 搜索词（JSON格式） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 配置数据模型

### 1. SearchConfig 数据结构

```python
@dataclass
class SearchConfig:
    # 基本配置
    repo_path: str                    # 代码仓库路径
    search_terms: Union[List[str], str]  # 搜索词
    
    # 文件过滤配置
    file_extensions: List[str] = field(default_factory=list)  # 文件扩展名
    exclude_dirs: List[str] = field(default_factory=lambda: [  # 排除目录
        '.git', '.svn', 'node_modules', '__pycache__', 'dist', 'build'
    ])
    exclude_files: List[str] = field(default_factory=list)   # 排除文件
    
    # 搜索配置
    is_regex: bool = False           # 是否正则表达式
    enable_second_check: bool = True  # 是否启用二次验证
    search_strategy: str = "auto"     # 搜索策略
    
    # 性能配置
    max_workers: int = 4             # 最大工作线程数
    
    # 输出配置
    db_path: str = "db/search_results.db"    # 数据库路径
    excel_path: str = "search_results.xlsx"  # Excel输出路径
    max_excel_rows: int = 1000000            # Excel最大行数
    
    # 日志配置
    log_level: str = "INFO"          # 日志级别
```

### 2. 配置验证规则

```python
def validate_config(config: SearchConfig) -> List[str]:
    """
    验证配置有效性
    
    Returns:
        错误信息列表，空列表表示验证通过
    """
    errors = []
    
    # 验证必需字段
    if not config.repo_path:
        errors.append("repo_path is required")
    
    if not config.search_terms:
        errors.append("search_terms is required")
    
    # 验证路径存在性
    if config.repo_path and not os.path.exists(config.repo_path):
        errors.append(f"repo_path does not exist: {config.repo_path}")
    
    # 验证数值范围
    if config.max_workers <= 0:
        errors.append("max_workers must be positive")
    
    if config.max_excel_rows <= 0:
        errors.append("max_excel_rows must be positive")
    
    # 验证枚举值
    valid_strategies = ["auto", "grep", "python"]
    if config.search_strategy not in valid_strategies:
        errors.append(f"invalid search_strategy: {config.search_strategy}")
    
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.log_level not in valid_log_levels:
        errors.append(f"invalid log_level: {config.log_level}")
    
    return errors
```

## 业务对象模型

### 1. SearchResult 模型

```python
@dataclass
class SearchResult:
    """搜索结果数据模型"""
    file_path: str          # 文件路径
    line_number: int        # 行号
    matched_content: str    # 匹配内容
    search_terms: str       # 搜索词（JSON字符串）
    created_at: Optional[datetime] = None  # 创建时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'file_path': self.file_path,
            'line_number': self.line_number,
            'matched_content': self.matched_content,
            'search_terms': self.search_terms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """从字典创建对象"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            file_path=data['file_path'],
            line_number=data['line_number'],
            matched_content=data['matched_content'],
            search_terms=data['search_terms'],
            created_at=created_at
        )
```

### 2. SearchStatistics 模型

```python
@dataclass
class SearchStatistics:
    """搜索统计信息模型"""
    total_files_scanned: int = 0      # 扫描文件总数
    total_matches_found: int = 0      # 找到匹配总数
    search_duration: float = 0.0      # 搜索耗时（秒）
    strategy_used: str = ""           # 使用的搜索策略
    validation_enabled: bool = False  # 是否启用验证
    validation_passed: int = 0        # 验证通过数量
    validation_failed: int = 0        # 验证失败数量
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @property
    def files_per_second(self) -> float:
        """计算每秒处理文件数"""
        if self.search_duration > 0:
            return self.total_files_scanned / self.search_duration
        return 0.0
    
    @property
    def validation_accuracy(self) -> float:
        """计算验证准确率"""
        total_validated = self.validation_passed + self.validation_failed
        if total_validated > 0:
            return self.validation_passed / total_validated
        return 0.0
```

## 数据传输模型

### 1. API 请求模型

```python
@dataclass
class SearchRequest:
    """搜索请求模型"""
    repo_path: str
    search_terms: Union[str, List[str]]
    file_extensions: Optional[List[str]] = None
    exclude_dirs: Optional[List[str]] = None
    is_regex: bool = False
    enable_validation: bool = True
    
    def to_config(self) -> SearchConfig:
        """转换为搜索配置"""
        return SearchConfig(
            repo_path=self.repo_path,
            search_terms=self.search_terms,
            file_extensions=self.file_extensions or [],
            exclude_dirs=self.exclude_dirs or [],
            is_regex=self.is_regex,
            enable_second_check=self.enable_validation
        )
```

### 2. API 响应模型

```python
@dataclass
class SearchResponse:
    """搜索响应模型"""
    success: bool
    message: str
    results: List[SearchResult]
    statistics: SearchStatistics
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'message': self.message,
            'results': [result.to_dict() for result in self.results],
            'statistics': self.statistics.to_dict(),
            'errors': self.errors
        }
```

## 缓存数据模型

### 1. FileMetadata 模型

```python
@dataclass
class FileMetadata:
    """文件元数据模型"""
    file_path: str
    file_size: int
    modified_time: float
    encoding: str = "utf-8"
    line_count: int = 0
    
    def is_modified_since(self, timestamp: float) -> bool:
        """检查文件是否在指定时间后修改"""
        return self.modified_time > timestamp
```

### 2. SearchCache 模型

```python
@dataclass
class SearchCache:
    """搜索缓存模型"""
    cache_key: str                    # 缓存键
    search_terms: str                 # 搜索词
    results: List[SearchResult]       # 缓存结果
    created_at: datetime              # 创建时间
    expires_at: datetime              # 过期时间
    
    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        return datetime.now() > self.expires_at
    
    @classmethod
    def create_cache_key(cls, repo_path: str, search_terms: Union[str, List[str]], 
                        is_regex: bool) -> str:
        """创建缓存键"""
        import hashlib
        content = f"{repo_path}:{search_terms}:{is_regex}"
        return hashlib.md5(content.encode()).hexdigest()
```

## 导出数据模型

### 1. ExcelExportConfig 模型

```python
@dataclass
class ExcelExportConfig:
    """Excel导出配置模型"""
    output_path: str
    max_rows_per_sheet: int = 1000000
    sheet_name_prefix: str = "SearchResults"
    include_headers: bool = True
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    def get_sheet_name(self, sheet_index: int) -> str:
        """获取工作表名称"""
        if sheet_index == 0:
            return self.sheet_name_prefix
        return f"{self.sheet_name_prefix}_{sheet_index + 1}"
```

### 2. ExportResult 模型

```python
@dataclass
class ExportResult:
    """导出结果模型"""
    success: bool
    output_files: List[str]
    total_records: int
    export_duration: float
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
```

## 数据验证

### 1. 数据类型验证

```python
def validate_search_result(result: Dict[str, Any]) -> bool:
    """验证搜索结果数据格式"""
    required_fields = ['file_path', 'line_number', 'matched_content', 'search_terms']
    
    # 检查必需字段
    for field in required_fields:
        if field not in result:
            return False
    
    # 检查数据类型
    if not isinstance(result['file_path'], str):
        return False
    
    if not isinstance(result['line_number'], int) or result['line_number'] < 1:
        return False
    
    if not isinstance(result['matched_content'], str):
        return False
    
    if not isinstance(result['search_terms'], str):
        return False
    
    return True
```

### 2. 业务规则验证

```python
def validate_business_rules(result: SearchResult, config: SearchConfig) -> List[str]:
    """验证业务规则"""
    errors = []
    
    # 文件路径应在仓库路径下
    if not result.file_path.startswith(config.repo_path):
        errors.append("File path is outside repository")
    
    # 行号应该大于0
    if result.line_number <= 0:
        errors.append("Line number must be positive")
    
    # 匹配内容不应为空
    if not result.matched_content.strip():
        errors.append("Matched content cannot be empty")
    
    return errors
```

## 总结

数据模型规范定义了Hello-Scan-Code系统中所有数据结构的标准格式，确保了数据的一致性和完整性。通过明确的模型定义和验证规则，系统能够可靠地处理各种数据场景，为功能扩展和系统集成提供了坚实的基础。